"""
IT-DAS Vokabeltrainer - Hauptanwendung

Ein Multiple-Choice-Vokabeltest für IT-Begriffe mit:
- Kategorienfilter (Mehrfachauswahl)
- Quiz-Logik mit Mehrfachantworten
- Spaced Repetition System
- Highscore-System
- Cyberpunk-Design mit Matrix-Regen-Effekt

Autor: IT-DAS Team
Version: 2.0
"""

import PySimpleGUI as sg
import random
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

# Eigene Module importieren
from database import get_datenbank

# ============================================================================
# KONFIGURATION
# ============================================================================

# Pfade für Daten
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VOKABELN_DATEI = os.path.join(SCRIPT_DIR, "vokabeln.json")

# Design-Konstanten (Cyberpunk-Style)
HINTERGRUND_FARBE = "#0a0a0a"  # Sehr dunkles Grau
TEXT_FARBE = "#00ff00"        # Grüne Schrift (Matrix-Stil)
AKZENT_FARBE = "#00cc00"       # Hellgrün für Akzente
FEHLER_FARBE = "#ff4444"       # Rot für Fehler
ERFOLG_FARBE = "#00ff88"       # Hellgrün für Erfolg
RAHMEN_FARBE = "#1a1a1a"       # Dunkler Rahmen
TRANSPARENZ = 0.85             # Gleichmäßige Transparenz

# Matrix-Regen-Konfiguration
MATRIX_ZEICHEN = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MATRIX_GESCHWINDIGKEIT = 0.08  # 25% langsamer als Standard (Standard wäre ~0.1)
MATRIX_DICHTE = 0.05           # Dichte der fallenden Zeichen
MATRIX_LAENGE = 20             # Maximale Länge der fallenden Ströme

# ============================================================================
# MATRIX-REGEN-EFFEKT (Hintergrundanimation)
# ============================================================================

class MatrixRegen:
    """
    Erzeugt einen Matrix-Regen-Effekt im Hintergrund.
    Der Effekt läuft durchgehend ohne Unterbrechung und ist 25% langsamer.
    """
    
    def __init__(self, canvas_size: tuple = (800, 600)):
        self.canvas_size = canvas_size
        self.width, self.height = canvas_size
        self.drops = []
        self.characters = MATRIX_ZEICHEN
        self.speed = MATRIX_GESCHWINDIGKEIT
        self.density = MATRIX_DICHTE
        self.max_length = MATRIX_LAENGE
        
        # Initialisiere Tropfen
        self._init_drops()
    
    def _init_drops(self):
        """Initialisiert die fallenden Zeichen-Tropfen."""
        import random
        num_drops = int(self.width * self.density)
        self.drops = []
        for _ in range(num_drops):
            self.drops.append({
                'x': random.randint(0, self.width - 1),
                'y': random.randint(-100, 0),
                'length': random.randint(5, self.max_length),
                'speed': random.uniform(self.speed * 0.5, self.speed * 1.5),
                'chars': []
            })
    
    def update(self):
        """Aktualisiert die Position der Tropfen."""
        import random
        for drop in self.drops:
            # Bewege Tropfen nach unten
            drop['y'] += drop['speed'] * 10
            
            # Wenn Tropfen unten angekommen, zurücsetzen
            if drop['y'] > self.height + drop['length']:
                drop['y'] = random.randint(-100, 0)
                drop['x'] = random.randint(0, self.width - 1)
                drop['length'] = random.randint(5, self.max_length)
                drop['speed'] = random.uniform(self.speed * 0.5, self.speed * 1.5)
                drop['chars'] = []
            
            # Zeichen für den Tropfen generieren
            if not drop['chars'] or len(drop['chars']) < drop['length']:
                drop['chars'] = [
                    self.characters[random.randint(0, len(self.characters) - 1)]
                    for _ in range(drop['length'])
                ]
    
    def draw(self, graph: sg.Graph) -> None:
        """
        Zeichnet den Matrix-Regen auf das Graph-Element.
        
        Args:
            graph: PySimpleGUI Graph-Element
        """
        graph.erase()
        
        # Hintergrund leicht aufhellen für bessere Lesbarkeit
        graph.draw_rectangle(
            (0, 0), (self.width, self.height),
            fill_color=HINTERGRUND_FARBE
        )
        
        # Tropfen zeichnen
        for drop in self.drops:
            x = drop['x']
            y_start = drop['y']
            
            # Kopf des Tropfens (hellgrün)
            if 0 <= y_start < self.height and 0 <= x < self.width:
                char = drop['chars'][0] if drop['chars'] else random.choice(self.characters)
                graph.draw_text(
                    char,
                    (x, y_start),
                    color=TEXT_FARBE,
                    font=('Consolas', 14)
                )
            
            # Schwanz des Tropfens (dunkler werdend)
            for i, char in enumerate(drop['chars'][1:], 1):
                y = y_start + i * 14
                if y >= self.height:
                    break
                
                # Farbe wird dunkler je länger der Schwanz
                alpha = max(0, 1 - (i / drop['length']))
                color_value = int(255 * alpha)
                color = f"#{color_value:02x}{color_value:02x}00"
                
                graph.draw_text(
                    char,
                    (x, y),
                    color=color,
                    font=('Consolas', 14)
                )


# ============================================================================
# VOKABELN-VERWALTUNG
# ============================================================================

class VokabelnVerwaltung:
    """
    Verwaltet das Laden und Filtern von Vokabeln aus der JSON-Datei.
    """
    
    def __init__(self):
        self.vokabeln = self._lade_vokabeln()
        self.verfuegbare_kategorien = self._get_verfuegbare_kategorien()
    
    def _lade_vokabeln(self) -> Dict[str, Any]:
        """Lädt die Vokabeln aus der JSON-Datei."""
        try:
            with open(VOKABELN_DATEI, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            sg.popup_error(f"Fehler beim Laden der Vokabeln: {e}")
            # Leere Struktur zurückgeben
            return {
                "version": "1.0",
                "kategorien": [],
                "fragen": []
            }
    
    def _get_verfuegbare_kategorien(self) -> List[str]:
        """Gibt eine Liste aller verfügbaren Kategorien zurück."""
        kategorien_set = set()
        
        # Kategorien aus der JSON-Datei extrahieren
        if "kategorien" in self.vokabeln:
            kategorien_set.update(self.vokabeln["kategorien"])
        
        # Kategorien aus den Fragen extrahieren
        if "fragen" in self.vokabeln:
            for frage in self.vokabeln["fragen"]:
                if "kategorien" in frage:
                    kategorien_set.update(frage["kategorien"])
        
        # Sortieren und "Alle" hinzufügen
        return ["Alle"] + sorted(list(kategorien_set))
    
    def get_fragen(self, ausgewählte_kategorien: List[str] = None) -> List[Dict[str, Any]]:
        """
        Gibt gefilterte Fragen zurück basierend auf den ausgewählten Kategorien.
        
        Args:
            ausgewählte_kategorien: Liste der ausgewählten Kategorien
                                   Wenn None oder leer, werden alle Fragen zurückgegeben
                                   Wenn "Alle" enthalten ist, werden alle Fragen zurückgegeben
        
        Returns:
            Liste der gefilterten Fragen
        """
        if not ausgewählte_kategorien or "Alle" in ausgewählte_kategorien:
            return self.vokabeln.get("fragen", [])
        
        gefilterte_fragen = []
        for frage in self.vokabeln.get("fragen", []):
            # Prüfen, ob die Frage zu einer der ausgewählten Kategorien gehört
            frage_kategorien = frage.get("kategorien", [])
            if any(kat in ausgewählte_kategorien for kat in frage_kategorien):
                gefilterte_fragen.append(frage)
        
        return gefilterte_fragen
    
    def get_zufällige_frage(self, ausgewählte_kategorien: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Gibt eine zufällige Frage aus den ausgewählten Kategorien zurück.
        
        Args:
            ausgewählte_kategorien: Liste der ausgewählten Kategorien
        
        Returns:
            Zufällige Frage oder None, wenn keine Fragen verfügbar
        """
        fragen = self.get_fragen(ausgewählte_kategorien)
        if not fragen:
            return None
        return random.choice(fragen)
    
    def get_antwortmöglichkeiten(self, frage: Dict[str, Any], anzahl: int = 4) -> List[str]:
        """
        Generiert Antwortmöglichkeiten für eine Frage.
        
        Args:
            frage: Die Frage
            anzahl: Anzahl der Antwortmöglichkeiten (Standard: 4)
        
        Returns:
            Liste der Antwortmöglichkeiten (gemischt)
        """
        richtige_antworten = frage.get("antworten", [])
        falsche_antworten = frage.get("falsche_antworten", [])
        
        # Alle Antworten sammeln
        alle_antworten = richtige_antworten.copy()
        
        # Falsche Antworten hinzufügen (so viele wie nötig)
        benötigte_falsche = anzahl - len(richtige_antworten)
        if benötigte_falsche > 0:
            # Wenn nicht genug falsche Antworten, wiederhole einige
            verfügbare_falsche = falsche_antworten * (benötigte_falsche // len(falsche_antworten) + 1)
            alle_antworten.extend(verfügbare_falsche[:benötigte_falsche])
        
        # Mischen und zurückgeben
        random.shuffle(alle_antworten)
        return alle_antworten[:anzahl]


# ============================================================================
# QUIZ-LOGIK
# ============================================================================

class QuizLogik:
    """
    Verwaltet die Quiz-Logik inkl. Punktevergabe und Antwortprüfung.
    """
    
    def __init__(self, vokabeln_verwaltung: VokabelnVerwaltung, datenbank):
        self.vokabeln = vokabeln_verwaltung
        self.db = datenbank
        self.aktuelle_frage = None
        self.ausgewählte_antworten = []
        self.punkte = 0
        self.fragen_anzahl = 0
        self.richtige_antworten = 0
        self.aktuelle_kategorien = ["Alle"]
        self.nutzername = None
    
    def set_nutzername(self, nutzername: str):
        """Setzt den Nutzernamen für die aktuelle Session."""
        self.nutzername = nutzername
        # Nutzer anlegen, falls nicht existiert
        if nutzername and not self.db.nutzer_existiert(nutzername):
            self.db.nutzer_anlegen(nutzername)
    
    def set_kategorien(self, kategorien: List[str]):
        """Setzt die ausgewählten Kategorien."""
        self.aktuelle_kategorien = kategorien if kategorien else ["Alle"]
    
    def neue_frage(self) -> Optional[Dict[str, Any]]:
        """
        Lädt eine neue zufällige Frage.
        
        Returns:
            Die neue Frage oder None, wenn keine Fragen verfügbar
        """
        self.aktuelle_frage = self.vokabeln.get_zufällige_frage(self.aktuelle_kategorien)
        if self.aktuelle_frage:
            self.ausgewählte_antworten = []
        return self.aktuelle_frage
    
    def get_antwortmöglichkeiten(self, anzahl: int = 4) -> List[str]:
        """Gibt die Antwortmöglichkeiten für die aktuelle Frage zurück."""
        if not self.aktuelle_frage:
            return []
        return self.vokabeln.get_antwortmöglichkeiten(self.aktuelle_frage, anzahl)
    
    def toggle_antwort(self, antwort: str):
        """
        Fügt eine Antwort zur Auswahl hinzu oder entfernt sie.
        
        Args:
            antwort: Die Antwort, die getoggled werden soll
        """
        if antwort in self.ausgewählte_antworten:
            self.ausgewählte_antworten.remove(antwort)
        else:
            self.ausgewählte_antworten.append(antwort)
    
    def prüfe_antworten(self) -> Dict[str, Any]:
        """
        Prüft die ausgewählten Antworten.
        
        Returns:
            Dictionary mit:
            - richtig: bool (ob alle ausgewählten Antworten richtig sind)
            - alle_richtig: bool (ob alle richtigen Antworten ausgewählt wurden)
            - teilweise_richtig: bool (ob einige richtige Antworten ausgewählt wurden)
            - punkte_erhalten: int (erhaltene Punkte)
            - richtige_antworten: Liste der richtigen Antworten
            - falsche_auswahl: Liste der falsch ausgewählten Antworten
            - fehlende_antworten: Liste der nicht ausgewählten richtigen Antworten
        """
        if not self.aktuelle_frage:
            return {
                "richtig": False,
                "alle_richtig": False,
                "teilweise_richtig": False,
                "punkte_erhalten": 0,
                "richtige_antworten": [],
                "falsche_auswahl": [],
                "fehlende_antworten": []
            }
        
        richtige_antworten = self.aktuelle_frage.get("antworten", [])
        mehrfachantwort = self.aktuelle_frage.get("mehrfachantwort", False)
        
        # Prüfen, ob alle ausgewählten Antworten richtig sind
        alle_ausgewählt_richtig = all(antwort in richtige_antworten for antwort in self.ausgewählte_antworten)
        
        # Prüfen, ob alle richtigen Antworten ausgewählt wurden
        alle_richtig_ausgewählt = all(antwort in self.ausgewählte_antworten for antwort in richtige_antworten)
        
        # Falsche Auswahl
        falsche_auswahl = [antwort for antwort in self.ausgewählte_antworten if antwort not in richtige_antworten]
        
        # Fehlende richtige Antworten
        fehlende_antworten = [antwort for antwort in richtige_antworten if antwort not in self.ausgewählte_antworten]
        
        # Punkte berechnen
        punkte_erhalten = 0
        if alle_ausgewählt_richtig and alle_richtig_ausgewählt:
            # Alle richtigen Antworten ausgewählt und keine falschen
            punkte_erhalten = len(richtige_antworten)
        elif alle_ausgewählt_richtig and len(self.ausgewählte_antworten) > 0:
            # Einige richtige Antworten ausgewählt, keine falschen
            punkte_erhalten = len(self.ausgewählte_antworten)
        elif not mehrfachantwort and len(self.ausgewählte_antworten) == 1:
            # Single-Choice: Eine Antwort ausgewählt
            if self.ausgewählte_antworten[0] in richtige_antworten:
                punkte_erhalten = 1
        
        # Statistiken aktualisieren
        self.fragen_anzahl += 1
        if punkte_erhalten > 0:
            self.richtige_antworten += 1
        
        # Punkte aktualisieren
        self.punkte += punkte_erhalten
        
        # Spaced Repetition aktualisieren (falls Nutzer angemeldet)
        if self.nutzername and self.aktuelle_frage:
            frage_id = self.aktuelle_frage.get("id", 0)
            richtig = punkte_erhalten > 0
            self.db.aktualisiere_spaced_repetition(self.nutzername, frage_id, richtig)
        
        # Highscore aktualisieren
        if self.nutzername:
            # Aktualisiere Highscore nach jeder Frage (oder nur am Ende?)
            pass
        
        return {
            "richtig": alle_ausgewählt_richtig and alle_richtig_ausgewählt,
            "alle_richtig": alle_richtig_ausgewählt,
            "teilweise_richtig": (len(self.ausgewählte_antworten) > 0 and 
                                (alle_ausgewählt_richtig or len(fehlende_antworten) < len(richtige_antworten))),
            "punkte_erhalten": punkte_erhalten,
            "richtige_antworten": richtige_antworten,
            "falsche_auswahl": falsche_auswahl,
            "fehlende_antworten": fehlende_antworten
        }
    
    def beende_session(self):
        """Beendet die aktuelle Quiz-Session und speichert die Daten."""
        if self.nutzername:
            # Nutzer-Session aktualisieren
            self.db.aktualisiere_nutzer_session(
                self.nutzername,
                self.punkte,
                self.fragen_anzahl,
                self.richtige_antworten
            )
            
            # Highscore aktualisieren
            self.db.aktualisiere_highscore(self.nutzername, self.punkte)
            
            # Highscore pro Kategorie aktualisieren
            for kategorie in self.aktuelle_kategorien:
                if kategorie != "Alle":
                    self.db.aktualisiere_highscore(self.nutzername, self.punkte, kategorie)
        
        # Zurücksetzen
        self.punkte = 0
        self.fragen_anzahl = 0
        self.richtige_antworten = 0
    
    def get_statistiken(self) -> Dict[str, Any]:
        """Gibt die aktuellen Session-Statistiken zurück."""
        return {
            "punkte": self.punkte,
            "fragen_anzahl": self.fragen_anzahl,
            "richtige_antworten": self.richtige_antworten,
            "erfolgsquote": (self.richtige_antworten / self.fragen_anzahl * 100) if self.fragen_anzahl > 0 else 0
        }


# ============================================================================
# HAUPTPROGRAMM
# ============================================================================

class ITDASApp:
    """
    Hauptanwendung des IT-DAS Vokabeltrainers.
    """
    
    def __init__(self):
        # Initialisiere Komponenten
        self.vokabeln = VokabelnVerwaltung()
        self.db = get_datenbank()
        self.quiz = QuizLogik(self.vokabeln, self.db)
        
        # Matrix-Regen initialisieren
        self.matrix_regen = MatrixRegen((800, 600))
        
        # Fenster-Status
        self.fenster_aktiv = False
        self.quiz_aktiv = False
        
        # Erstelle Hauptfenster
        self.window = self._erstelle_hauptfenster()
        self.fenster_aktiv = True
    
    def _erstelle_hauptfenster(self) -> sg.Window:
        """Erstellt das Hauptfenster mit Startbildschirm."""
        
        # Matrix-Regen Graph
        matrix_graph = sg.Graph(
            canvas_size=(800, 600),
            graph_bottom_left=(0, 0),
            graph_top_right=(800, 600),
            key="-MATRIX-GRAPH-",
            background_color=HINTERGRUND_FARBE,
            enable_events=True
        )
        
        # Kategorien-Checkboxen erstellen
        kategorien_layout = []
        for i, kategorie in enumerate(self.vokabeln.verfuegbare_kategorien):
            if i % 3 == 0:
                kategorien_layout.append([])
            kategorien_layout[-1].append(
                sg.Checkbox(
                    kategorie,
                    key=f"-KATEGORIE-{kategorie}-",
                    default=(kategorie == "Alle"),
                    background_color=HINTERGRUND_FARBE,
                    text_color=TEXT_FARBE,
                    enable_events=True
                )
            )
        
        # Layout für Startbildschirm
        start_layout = [
            [sg.Text("IT-DAS 🎯", font=("Arial", 32, "bold"), 
                     text_color=TEXT_FARBE, background_color=HINTERGRUND_FARBE, 
                     justification="center", pad=(0, 20))],
            [sg.Text("Vokabeltrainer für IT-Begriffe", font=("Arial", 16),
                     text_color=AKZENT_FARBE, background_color=HINTERGRUND_FARBE,
                     justification="center", pad=(0, 10))],
            [sg.HorizontalSeparator(color=AKZENT_FARBE, background_color=HINTERGRUND_FARBE, pad=(20, 20))],
            
            [sg.Text("Nutzername:", font=("Arial", 14), text_color=TEXT_FARBE, 
                     background_color=HINTERGRUND_FARBE, size=(12, 1))],
            [sg.Input(
                key="-NUTZERNAME-",
                size=(30, 1),
                font=("Arial", 14),
                background_color=RAHMEN_FARBE,
                text_color=TEXT_FARBE,
                tooltip="Gib deinen Nutzernamen ein"
            )],
            [sg.Text("Wähle Kategorien:", font=("Arial", 14), text_color=TEXT_FARBE,
                     background_color=HINTERGRUND_FARBE, pad=(0, 10))],
            
            # Kategorien in Scrollbox (falls zu viele)
            [sg.Frame(
                "Kategorien",
                layout=kategorien_layout,
                background_color=HINTERGRUND_FARBE,
                border_width=1,
                relief=sg.RELIEF_FLAT
            )],
            
            [sg.HorizontalSeparator(color=AKZENT_FARBE, background_color=HINTERGRUND_FARBE, pad=(20, 20))],
            
            [sg.Button(
                "Quiz Starten",
                key="-START-",
                size=(20, 2),
                font=("Arial", 14, "bold"),
                button_color=(TEXT_FARBE, HINTERGRUND_FARBE),
                border_width=2,
                tooltip="Starte das Quiz mit den ausgewählten Kategorien"
            )],
            [sg.Button(
                "Highscores",
                key="-HIGHSCORES-",
                size=(20, 1),
                font=("Arial", 12),
                button_color=(AKZENT_FARBE, HINTERGRUND_FARBE),
                border_width=1
            )],
            [sg.Button(
                "Beenden",
                key="-BEENDEN-",
                size=(20, 1),
                font=("Arial", 12),
                button_color=(FEHLER_FARBE, HINTERGRUND_FARBE),
                border_width=1
            )],
            
            [sg.Text(
                "IT-DAS - Lerne IT-Begriffe spielerisch! | 100% kostenlos & Open-Source",
                font=("Arial", 10),
                text_color="#666666",
                background_color=HINTERGRUND_FARBE,
                justification="center",
                pad=(0, 20)
            )]
        ]
        
        # Hauptlayout mit Matrix-Regen im Hintergrund
        layout = [
            [matrix_graph],
            [sg.Column(
                start_layout,
                background_color=HINTERGRUND_FARBE,
                element_justification="center",
                vertical_alignment="center",
                key="-START-COLUMN-",
                visible=True
            )],
            [sg.Column(
                self._erstelle_quiz_layout(),
                background_color=HINTERGRUND_FARBE,
                element_justification="center",
                vertical_alignment="center",
                key="-QUIZ-COLUMN-",
                visible=False
            )]
        ]
        
        # Fenster erstellen
        window = sg.Window(
            "IT-DAS Vokabeltrainer",
            layout,
            size=(800, 600),
            location=(100, 100),
            background_color=HINTERGRUND_FARBE,
            no_titlebar=False,
            keep_on_top=False,
            finalize=True,
            resizable=True,
            icon=None
        )
        
        return window
    
    def _erstelle_quiz_layout(self) -> List[List[sg.Element]]:
        """Erstellt das Layout für das Quiz."""
        return [
            [sg.Text(
                "IT-DAS Quiz 🎯",
                font=("Arial", 24, "bold"),
                text_color=TEXT_FARBE,
                background_color=HINTERGRUND_FARBE,
                justification="center",
                key="-QUIZ-TITEL-",
                pad=(0, 10)
            )],
            [sg.HorizontalSeparator(color=AKZENT_FARBE, background_color=HINTERGRUND_FARBE, pad=(20, 10))],
            
            # Frage
            [sg.Text(
                "",
                font=("Arial", 16),
                text_color=TEXT_FARBE,
                background_color=HINTERGRUND_FARBE,
                justification="center",
                size=(70, 3),
                key="-FRAGE-TEXT-",
                pad=(20, 10)
            )],
            
            # Kategorie und Schwierigkeit
            [sg.Text(
                "",
                font=("Arial", 12),
                text_color=AKZENT_FARBE,
                background_color=HINTERGRUND_FARBE,
                justification="center",
                key="-FRAGE-INFO-",
                pad=(20, 5)
            )],
            
            [sg.HorizontalSeparator(color=AKZENT_FARBE, background_color=HINTERGRUND_FARBE, pad=(20, 10))],
            
            # Antwortmöglichkeiten (Checkboxen für Mehrfachauswahl)
            [sg.Text(
                "Wähle alle richtigen Antworten:",
                font=("Arial", 14),
                text_color=TEXT_FARBE,
                background_color=HINTERGRUND_FARBE,
                pad=(20, 5)
            )],
            
            [sg.Column(
                [
                    [sg.Checkbox(
                        "",
                        key=f"-ANTWORT-{i}-",
                        font=("Arial", 14),
                        text_color=TEXT_FARBE,
                        background_color=HINTERGRUND_FARBE,
                        size=(60, 1),
                        enable_events=True,
                        pad=(10, 5)
                    )] for i in range(4)
                ],
                key="-ANTWORTEN-COLUMN-",
                background_color=HINTERGRUND_FARBE,
                pad=(20, 10)
            )],
            
            [sg.HorizontalSeparator(color=AKZENT_FARBE, background_color=HINTERGRUND_FARBE, pad=(20, 10))],
            
            # Ergebnis-Anzeige
            [sg.Text(
                "",
                font=("Arial", 14),
                text_color=TEXT_FARBE,
                background_color=HINTERGRUND_FARBE,
                justification="center",
                size=(70, 2),
                key="-ERGEBNIS-TEXT-",
                pad=(20, 5)
            )],
            
            # Punkte-Anzeige
            [sg.Text(
                "Punkte: 0 | Fragen: 0 | Richtig: 0",
                font=("Arial", 14),
                text_color=TEXT_FARBE,
                background_color=HINTERGRUND_FARBE,
                justification="center",
                key="-PUNKTE-ANZEIGE-",
                pad=(20, 5)
            )],
            
            [sg.HorizontalSeparator(color=AKZENT_FARBE, background_color=HINTERGRUND_FARBE, pad=(20, 10))],
            
            # Aktions-Buttons
            [sg.Column(
                [
                    [sg.Button(
                        "Antwort prüfen",
                        key="-PRUEFEN-",
                        size=(20, 1),
                        font=("Arial", 12, "bold"),
                        button_color=(TEXT_FARBE, HINTERGRUND_FARBE),
                        border_width=2,
                        disabled=True,
                        pad=(10, 5)
                    )],
                    [sg.Button(
                        "Nächste Frage",
                        key="-NAECHSTE-",
                        size=(20, 1),
                        font=("Arial", 12, "bold"),
                        button_color=(AKZENT_FARBE, HINTERGRUND_FARBE),
                        border_width=2,
                        pad=(10, 5)
                    )],
                    [sg.Button(
                        "Quiz beenden",
                        key="-QUIZ-BEENDEN-",
                        size=(20, 1),
                        font=("Arial", 12),
                        button_color=(FEHLER_FARBE, HINTERGRUND_FARBE),
                        border_width=1,
                        pad=(10, 5)
                    )]
                ],
                element_justification="center",
                background_color=HINTERGRUND_FARBE
            )]
        ]
    
    def _zeige_highscores(self):
        """Zeigt das Highscore-Fenster an."""
        highscores = self.db.get_highscores(limit=20)
        
        # Highscore-Layout
        layout = [
            [sg.Text(
                "🏆 IT-DAS Highscores 🏆",
                font=("Arial", 20, "bold"),
                text_color=TEXT_FARBE,
                background_color=HINTERGRUND_FARBE,
                justification="center",
                pad=(0, 20)
            )],
            [sg.HorizontalSeparator(color=AKZENT_FARBE, background_color=HINTERGRUND_FARBE, pad=(20, 10))],
            
            [sg.Text(
                "Globale Highscores",
                font=("Arial", 14, "bold"),
                text_color=TEXT_FARBE,
                background_color=HINTERGRUND_FARBE,
                pad=(20, 10)
            )],
            
            [sg.Table(
                values=[
                    [i+1, eintrag["nutzer"], eintrag["punkte"], eintrag["datum"]]
                    for i, eintrag in enumerate(highscores)
                ],
                headings=["Rang", "Nutzer", "Punkte", "Datum"],
                key="-HIGHSCORE-TABELLE-",
                font=("Arial", 12),
                text_color=TEXT_FARBE,
                background_color=HINTERGRUND_FARBE,
                header_text_color=TEXT_FARBE,
                header_background_color=RAHMEN_FARBE,
                num_rows=10,
                col_widths=[5, 20, 10, 25],
                pad=(20, 10)
            )],
            
            [sg.Button(
                "Zurück",
                key="-ZURUECK-",
                size=(20, 1),
                font=("Arial", 12),
                button_color=(AKZENT_FARBE, HINTERGRUND_FARBE),
                border_width=1,
                pad=(0, 20)
            )]
        ]
        
        # Fenster erstellen
        highscore_window = sg.Window(
            "IT-DAS Highscores",
            layout,
            size=(600, 500),
            background_color=HINTERGRUND_FARBE,
            finalize=True
        )
        
        # Event-Loop für Highscore-Fenster
        while True:
            event, values = highscore_window.read()
            if event == sg.WIN_CLOSED or event == "-ZURUECK-":
                break
        
        highscore_window.close()
    
    def _aktualisiere_antwort_buttons(self):
        """Aktualisiert die Antwort-Checkboxen mit den Antwortmöglichkeiten."""
        antworten = self.quiz.get_antwortmöglichkeiten()
        for i in range(4):
            if i < len(antworten):
                self.window[f"-ANTWORT-{i}-"].update(
                    text=antworten[i],
                    value=False
                )
            else:
                self.window[f"-ANTWORT-{i}-"].update(
                    text="",
                    value=False
                )
    
    def _zeige_frage(self):
        """Zeigt die aktuelle Frage an."""
        frage = self.quiz.neue_frage()
        if not frage:
            sg.popup_error("Keine Fragen in den ausgewählten Kategorien verfügbar!")
            return
        
        # Frage anzeigen
        self.window["-FRAGE-TEXT-"].update(frage["frage"])
        
        # Kategorie und Schwierigkeit anzeigen
        kategorien = ", ".join(frage.get("kategorien", []))
        schwierigkeit = frage.get("schwierigkeit", "⭐")
        self.window["-FRAGE-INFO-"].update(
            f"Kategorien: {kategorien} | Schwierigkeit: {schwierigkeit}"
        )
        
        # Antwortmöglichkeiten aktualisieren
        self._aktualisiere_antwort_buttons()
        
        # Ergebnis zurücksetzen
        self.window["-ERGEBNIS-TEXT-"].update("")
        
        # Prüfen-Button deaktivieren (bis Antwort ausgewählt)
        self.window["-PRUEFEN-"].update(disabled=True)
        
        # Quiz-Status
        self.quiz_aktiv = True
    
    def _prüfe_antworten(self):
        """Prüft die ausgewählten Antworten."""
        if not self.quiz_aktiv:
            return
        
        # Ausgewählte Antworten sammeln
        ausgewählte = []
        for i in range(4):
            if self.window[f"-ANTWORT-{i}-"].get():
                ausgewählte.append(self.window[f"-ANTWORT-{i}-"].DisplayText)
        
        # Antworten im Quiz-Objekt setzen
        self.quiz.ausgewählte_antworten = ausgewählte
        
        # Antworten prüfen
        ergebnis = self.quiz.prüfe_antworten()
        
        # Ergebnis anzeigen
        if ergebnis["richtig"]:
            self.window["-ERGEBNIS-TEXT-"].update(
                "✅ Richtig! 🎉",
                text_color=ERFOLG_FARBE
            )
        elif ergebnis["teilweise_richtig"]:
            self.window["-ERGEBNIS-TEXT-"].update(
                f"⚠️  Teilweise richtig! Richtige Antworten: {', '.join(ergebnis['richtige_antworten'])}",
                text_color="#ffff00"
            )
        else:
            self.window["-ERGEBNIS-TEXT-"].update(
                f"❌ Falsch! Richtige Antworten: {', '.join(ergebnis['richtige_antworten'])}",
                text_color=FEHLER_FARBE
            )
        
        # Punkte aktualisieren
        statistiken = self.quiz.get_statistiken()
        self.window["-PUNKTE-ANZEIGE-"].update(
            f"Punkte: {statistiken['punkte']} | "
            f"Fragen: {statistiken['fragen_anzahl']} | "
            f"Richtig: {statistiken['richtige_antworten']} "
            f"({statistiken['erfolgsquote']:.1f}%)"
        )
        
        # Prüfen-Button deaktivieren
        self.window["-PRUEFEN-"].update(disabled=True)
        
        # Nächste Frage-Button aktivieren
        self.window["-NAECHSTE-"].update(disabled=False)
    
    def run(self):
        """Haupt-Event-Loop der Anwendung."""
        
        while self.fenster_aktiv:
            # Matrix-Regen aktualisieren
            self.matrix_regen.update()
            self.window["-MATRIX-GRAPH-"].erase()
            self.matrix_regen.draw(self.window["-MATRIX-GRAPH-"])
            
            # Fenster-Events verarbeiten
            window, event, values = sg.read_all_windows(timeout=50)
            
            if event == sg.WIN_CLOSED:
                self.fenster_aktiv = False
                break
            
            # Hauptfenster-Events
            if window == self.window:
                if event == "-BEENDEN-":
                    self.fenster_aktiv = False
                    break
                
                elif event == "-START-":
                    # Nutzername prüfen
                    nutzername = values.get("-NUTZERNAME-", "").strip()
                    if not nutzername:
                        sg.popup_error("Bitte gib einen Nutzernamen ein!")
                        continue
                    
                    # Ausgewählte Kategorien sammeln
                    ausgewählte_kategorien = []
                    for kategorie in self.vokabeln.verfuegbare_kategorien:
                        if values.get(f"-KATEGORIE-{kategorie}-", False):
                            ausgewählte_kategorien.append(kategorie)
                    
                    if not ausgewählte_kategorien:
                        sg.popup_error("Bitte wähle mindestens eine Kategorie aus!")
                        continue
                    
                    # Quiz initialisieren
                    self.quiz.set_nutzername(nutzername)
                    self.quiz.set_kategorien(ausgewählte_kategorien)
                    
                    # Zum Quiz wechseln
                    self.window["-START-COLUMN-"].update(visible=False)
                    self.window["-QUIZ-COLUMN-"].update(visible=True)
                    self.quiz_aktiv = True
                    
                    # Erste Frage anzeigen
                    self._zeige_frage()
                
                elif event == "-HIGHSCORES-":
                    self._zeige_highscores()
                
                # Quiz-Events
                elif self.quiz_aktiv:
                    if event == "-QUIZ-BEENDEN-":
                        # Session beenden
                        self.quiz.beende_session()
                        self.quiz_aktiv = False
                        
                        # Zum Startbildschirm zurückkehren
                        self.window["-QUIZ-COLUMN-"].update(visible=False)
                        self.window["-START-COLUMN-"].update(visible=True)
                        
                        # Matrix-Regen zurücksetzen
                        self.matrix_regen = MatrixRegen((800, 600))
                    
                    elif event == "-NAECHSTE-":
                        # Nächste Frage anzeigen
                        self._zeige_frage()
                        self.window["-NAECHSTE-"].update(disabled=True)
                    
                    elif event == "-PRUEFEN-":
                        self._prüfe_antworten()
                    
                    # Antwort-Checkboxen
                    elif any(event.startswith(f"-ANTWORT-{i}-") for i in range(4)):
                        # Prüfen, ob mindestens eine Antwort ausgewählt ist
                        eine_ausgewählt = any(
                            values.get(f"-ANTWORT-{i}-", False) 
                            for i in range(4)
                        )
                        self.window["-PRUEFEN-"].update(disabled=not eine_ausgewählt)
                
                # Kategorien-Checkboxen (im Startbildschirm)
                elif any(event.startswith("-KATEGORIE-") for key in values):
                    # "Alle" deaktivieren, wenn andere Kategorien ausgewählt werden
                    alle_ausgewählt = values.get("-KATEGORIE-Alle-", False)
                    andere_ausgewählt = any(
                        values.get(f"-KATEGORIE-{kat}-", False) 
                        for kat in self.vokabeln.verfuegbare_kategorien 
                        if kat != "Alle"
                    )
                    
                    if alle_ausgewählt and andere_ausgewählt:
                        # "Alle" deaktivieren, wenn andere ausgewählt sind
                        self.window["-KATEGORIE-Alle-"].update(value=False)
                    elif not alle_ausgewählt and not andere_ausgewählt:
                        # "Alle" aktivieren, wenn keine ausgewählt ist
                        self.window["-KATEGORIE-Alle-"].update(value=True)
            
            # Fenster aktualisieren
            self.window.refresh()
        
        # Aufräumen
        self.window.close()
        print("IT-DAS Vokabeltrainer beendet.")


# ============================================================================
# PROGRAMM-START
# ============================================================================

if __name__ == "__main__":
    # Prüfen, ob PySimpleGUI installiert ist
    try:
        import PySimpleGUI
    except ImportError:
        print("Fehler: PySimpleGUI ist nicht installiert!")
        print("Installiere es mit: pip install PySimpleGUI==4.60.5")
        sys.exit(1)
    
    # Anwendung starten
    app = ITDASApp()
    app.run()
