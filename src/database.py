"""
IT-DAS Vokabeltrainer - Datenbankmodul

Verantwortlich für:
- Speicherung von Nutzerfortschritt
- Highscore-Verwaltung
- Spaced Repetition System (Wiederholungslogik)
- Nutzerprofile

Autor: IT-DAS Team
Version: 2.0
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Pfade für Daten
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DATEI = os.path.join(SCRIPT_DIR, "nutzer_daten.json")
HIGHSCORE_DATEI = os.path.join(SCRIPT_DIR, "highscore.json")
SPACED_REPETITION_DATEI = os.path.join(SCRIPT_DIR, "spaced_repetition.json")


class NutzerDatenbank:
    """
    Verwaltet alle nutzerbezogenen Daten inkl. Fortschritt und Spaced Repetition.
    """
    
    # Spaced Repetition Intervalle in Tagen
    SPACED_REPETITION_INTERVALLE = {
        1: 3,   # 1. richtige Antwort -> 3 Tage
        2: 5,   # 2. richtige Antwort -> 5 Tage
        3: 7,   # 3. richtige Antwort -> 7 Tage
        4: 30   # 4+ richtige Antworten -> 30 Tage
    }
    
    def __init__(self):
        """Initialisiert die Datenbank und lädt bestehende Daten."""
        self.nutzer_daten = self._lade_nutzer_daten()
        self.highscores = self._lade_highscores()
        self.spaced_repetition = self._lade_spaced_repetition()
    
    def _lade_nutzer_daten(self) -> Dict[str, Any]:
        """Lädt Nutzerdaten aus der JSON-Datei oder erstellt neue."""
        try:
            with open(DATABASE_DATEI, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Standardstruktur erstellen
            return {
                "nutzer": {},
                "statistiken": {
                    "gesamte_fragen": 0,
                    "richtige_antworten": 0,
                    "falsche_antworten": 0,
                    "durchschnittliche_punkte": 0.0
                }
            }
    
    def _speichere_nutzer_daten(self):
        """Speichert Nutzerdaten in die JSON-Datei."""
        with open(DATABASE_DATEI, "w", encoding="utf-8") as f:
            json.dump(self.nutzer_daten, f, indent=4, ensure_ascii=False)
    
    def _lade_highscores(self) -> Dict[str, Any]:
        """Lädt Highscore-Daten aus der JSON-Datei oder erstellt neue."""
        try:
            with open(HIGHSCORE_DATEI, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "global": [],
                "pro_kategorie": {}
            }
    
    def _speichere_highscores(self):
        """Speichert Highscore-Daten in die JSON-Datei."""
        with open(HIGHSCORE_DATEI, "w", encoding="utf-8") as f:
            json.dump(self.highscores, f, indent=4, ensure_ascii=False)
    
    def _lade_spaced_repetition(self) -> Dict[str, Any]:
        """Lädt Spaced Repetition Daten aus der JSON-Datei oder erstellt neue."""
        try:
            with open(SPACED_REPETITION_DATEI, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "nutzer": {}
            }
    
    def _speichere_spaced_repetition(self):
        """Speichert Spaced Repetition Daten in die JSON-Datei."""
        with open(SPACED_REPETITION_DATEI, "w", encoding="utf-8") as f:
            json.dump(self.spaced_repetition, f, indent=4, ensure_ascii=False)
    
    def nutzer_anlegen(self, nutzername: str, avatar: Optional[str] = None) -> bool:
        """
        Legt einen neuen Nutzer an.
        
        Args:
            nutzername: Eindeutiger Nutzername
            avatar: Optionales Avatar-Bild (Pfad oder URL)
            
        Returns:
            True, wenn Nutzer angelegt wurde; False, wenn bereits existiert
        """
        if nutzername in self.nutzer_daten["nutzer"]:
            return False
        
        self.nutzer_daten["nutzer"][nutzername] = {
            "avatar": avatar,
            "erstellt_am": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "letzte_anmeldung": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "punkte_gesamte": 0,
            "fragen_beantwortet": 0,
            "richtige_antworten": 0,
            "falsche_antworten": 0,
            "kategorien_fortschritt": {},
            "letzte_session": {
                "datum": None,
                "punkte": 0,
                "fragen": 0
            }
        }
        
        # Spaced Repetition für Nutzer initialisieren
        self.spaced_repetition["nutzer"][nutzername] = {
            "fragen": {},  # Frage-ID -> {richtig_beantwortet: int, naechste_wiederholung: str}
            "letzte_wiederholung": None
        }
        
        self._speichere_nutzer_daten()
        self._speichere_spaced_repetition()
        return True
    
    def nutzer_existiert(self, nutzername: str) -> bool:
        """Prüft, ob ein Nutzer existiert."""
        return nutzername in self.nutzer_daten["nutzer"]
    
    def get_nutzer_daten(self, nutzername: str) -> Optional[Dict[str, Any]]:
        """Gibt die Daten eines Nutzers zurück oder None, wenn nicht existiert."""
        return self.nutzer_daten["nutzer"].get(nutzername)
    
    def aktualisiere_nutzer_session(self, nutzername: str, punkte: int, fragen: int, richtige: int):
        """
        Aktualisiert die Session-Daten eines Nutzers.
        
        Args:
            nutzername: Name des Nutzers
            punkte: Punkte in dieser Session
            fragen: Anzahl der beantworteten Fragen
            richtige: Anzahl der richtigen Antworten
        """
        if nutzername not in self.nutzer_daten["nutzer"]:
            return
        
        nutzer = self.nutzer_daten["nutzer"][nutzername]
        nutzer["letzte_session"] = {
            "datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "punkte": punkte,
            "fragen": fragen
        }
        nutzer["letzte_anmeldung"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nutzer["punkte_gesamte"] += punkte
        nutzer["fragen_beantwortet"] += fragen
        nutzer["richtige_antworten"] += richtige
        nutzer["falsche_antworten"] += (fragen - richtige)
        
        # Statistiken aktualisieren
        self.nutzer_daten["statistiken"]["gesamte_fragen"] += fragen
        self.nutzer_daten["statistiken"]["richtige_antworten"] += richtige
        self.nutzer_daten["statistiken"]["falsche_antworten"] += (fragen - richtige)
        
        if fragen > 0:
            prozent = (richtige / fragen) * 100
            # Durchschnitt aktualisieren (gleitender Durchschnitt)
            alte_gesamte = self.nutzer_daten["statistiken"]["gesamte_fragen"] - fragen
            if alte_gesamte > 0:
                alter_durchschnitt = self.nutzer_daten["statistiken"]["durchschnittliche_punkte"]
                neuer_durchschnitt = (alter_durchschnitt * alte_gesamte + prozent) / self.nutzer_daten["statistiken"]["gesamte_fragen"]
            else:
                neuer_durchschnitt = prozent
            self.nutzer_daten["statistiken"]["durchschnittliche_punkte"] = neuer_durchschnitt
        
        self._speichere_nutzer_daten()
    
    def aktualisiere_highscore(self, nutzername: str, punkte: int, kategorie: Optional[str] = None):
        """
        Aktualisiert den Highscore für einen Nutzer.
        
        Args:
            nutzername: Name des Nutzers
            punkte: Erreichte Punkte
            kategorie: Optionale Kategorie für kategoriespezifischen Highscore
        """
        # Globalen Highscore aktualisieren
        neuer_eintrag = {
            "nutzer": nutzername,
            "punkte": punkte,
            "datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Prüfen, ob dieser Nutzer bereits in den Top 10 ist
        global_highscores = self.highscores["global"]
        
        # Nutzer-Einträge aktualisieren oder hinzufügen
        nutzer_gefunden = False
        for eintrag in global_highscores:
            if eintrag["nutzer"] == nutzername:
                if punkte > eintrag["punkte"]:
                    eintrag["punkte"] = punkte
                    eintrag["datum"] = neuer_eintrag["datum"]
                nutzer_gefunden = True
                break
        
        if not nutzer_gefunden:
            global_highscores.append(neuer_eintrag)
        
        # Nach Punkten sortieren und auf Top 10 begrenzen
        global_highscores.sort(key=lambda x: x["punkte"], reverse=True)
        self.highscores["global"] = global_highscores[:10]
        
        # Kategoriespezifischen Highscore aktualisieren
        if kategorie:
            if kategorie not in self.highscores["pro_kategorie"]:
                self.highscores["pro_kategorie"][kategorie] = []
            
            kat_highscores = self.highscores["pro_kategorie"][kategorie]
            nutzer_gefunden = False
            for eintrag in kat_highscores:
                if eintrag["nutzer"] == nutzername:
                    if punkte > eintrag["punkte"]:
                        eintrag["punkte"] = punkte
                        eintrag["datum"] = neuer_eintrag["datum"]
                    nutzer_gefunden = True
                    break
            
            if not nutzer_gefunden:
                kat_highscores.append(neuer_eintrag)
            
            kat_highscores.sort(key=lambda x: x["punkte"], reverse=True)
            self.highscores["pro_kategorie"][kategorie] = kat_highscores[:10]
        
        self._speichere_highscores()
    
    def get_highscores(self, kategorie: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Gibt die Highscore-Liste zurück.
        
        Args:
            kategorie: Optionale Kategorie (None für global)
            limit: Maximale Anzahl von Einträgen
            
        Returns:
            Liste der Highscore-Einträge
        """
        if kategorie:
            return self.highscores["pro_kategorie"].get(kategorie, [])[:limit]
        return self.highscores["global"][:limit]
    
    def get_spaced_repetition_daten(self, nutzername: str, frage_id: int) -> Dict[str, Any]:
        """
        Gibt die Spaced Repetition Daten für eine bestimmte Frage und Nutzer zurück.
        
        Args:
            nutzername: Name des Nutzers
            frage_id: ID der Frage
            
        Returns:
            Dictionary mit Spaced Repetition Daten
        """
        if nutzername not in self.spaced_repetition["nutzer"]:
            self.spaced_repetition["nutzer"][nutzername] = {
                "fragen": {},
                "letzte_wiederholung": None
            }
        
        nutzer_sr = self.spaced_repetition["nutzer"][nutzername]
        if frage_id not in nutzer_sr["fragen"]:
            nutzer_sr["fragen"][frage_id] = {
                "richtig_beantwortet": 0,
                "naechste_wiederholung": None,
                "letzte_beantwortung": None,
                "wiederholungs_count": 0
            }
        
        return nutzer_sr["fragen"][frage_id]
    
    def aktualisiere_spaced_repetition(self, nutzername: str, frage_id: int, richtig: bool):
        """
        Aktualisiert die Spaced Repetition Daten basierend auf der Antwort.
        
        Args:
            nutzername: Name des Nutzers
            frage_id: ID der Frage
            richtig: Ob die Antwort richtig war
        """
        sr_daten = self.get_spaced_repetition_daten(nutzername, frage_id)
        jetzt = datetime.now()
        
        if richtig:
            # Anzahl der richtigen Antworten in Folge erhöhen
            sr_daten["richtig_beantwortet"] += 1
            sr_daten["letzte_beantwortung"] = jetzt.strftime("%Y-%m-%d %H:%M:%S")
            
            # Nächstes Wiederholungsdatum berechnen
            count = sr_daten["richtig_beantwortet"]
            if count <= 4:
                tage = self.SPACED_REPETITION_INTERVALLE.get(count, 30)
            else:
                tage = 30  # Ab 4 richtigen Antworten immer 30 Tage
            
            sr_daten["naechste_wiederholung"] = (jetzt + timedelta(days=tage)).strftime("%Y-%m-%d %H:%M:%S")
            sr_daten["wiederholungs_count"] += 1
            
        else:
            # Bei falscher Antwort: Zurücksetzen auf 0 und sofortige Wiederholung
            sr_daten["richtig_beantwortet"] = 0
            sr_daten["letzte_beantwortung"] = jetzt.strftime("%Y-%m-%d %H:%M:%S")
            sr_daten["naechste_wiederholung"] = jetzt.strftime("%Y-%m-%d %H:%M:%S")  # Sofort
            sr_daten["wiederholungs_count"] += 1
        
        # Letzte Wiederholung für den Nutzer aktualisieren
        self.spaced_repetition["nutzer"][nutzername]["letzte_wiederholung"] = jetzt.strftime("%Y-%m-%d %H:%M:%S")
        self._speichere_spaced_repetition()
    
    def get_fragen_zur_wiederholung(self, nutzername: str) -> List[int]:
        """
        Gibt eine Liste von Frage-IDs zurück, die für Wiederholung fällig sind.
        
        Args:
            nutzername: Name des Nutzers
            
        Returns:
            Liste von Frage-IDs, die wiederholt werden sollten
        """
        if nutzername not in self.spaced_repetition["nutzer"]:
            return []
        
        jetzt = datetime.now()
        fällige_fragen = []
        
        for frage_id, sr_daten in self.spaced_repetition["nutzer"][nutzername]["fragen"].items():
            if sr_daten["naechste_wiederholung"]:
                naechste_wiederholung = datetime.strptime(
                    sr_daten["naechste_wiederholung"], "%Y-%m-%d %H:%M:%S"
                )
                if jetzt >= naechste_wiederholung:
                    fällige_fragen.append(frage_id)
        
        return fällige_fragen
    
    def get_statistiken(self, nutzername: Optional[str] = None) -> Dict[str, Any]:
        """
        Gibt Statistiken zurück (global oder für einen bestimmten Nutzer).
        
        Args:
            nutzername: Optional - wenn None, werden globale Statistiken zurückgegeben
            
        Returns:
            Dictionary mit Statistiken
        """
        if nutzername:
            if nutzername not in self.nutzer_daten["nutzer"]:
                return {}
            nutzer = self.nutzer_daten["nutzer"][nutzername]
            return {
                "punkte_gesamte": nutzer["punkte_gesamte"],
                "fragen_beantwortet": nutzer["fragen_beantwortet"],
                "richtige_antworten": nutzer["richtige_antworten"],
                "falsche_antworten": nutzer["falsche_antworten"],
                "erfolgsquote": (nutzer["richtige_antworten"] / nutzer["fragen_beantwortet"] * 100) if nutzer["fragen_beantwortet"] > 0 else 0,
                "letzte_session": nutzer["letzte_session"]
            }
        else:
            return self.nutzer_daten["statistiken"]


# Singleton-Instanz für einfache Nutzung
nutzer_datenbank = NutzerDatenbank()


def get_datenbank():
    """Gibt die globale Datenbank-Instanz zurück."""
    return nutzer_datenbank


if __name__ == "__main__":
    # Test der Datenbank
    db = get_datenbank()
    
    # Test: Nutzer anlegen
    db.nutzer_anlegen("Testnutzer", "avatar.png")
    
    # Test: Highscore aktualisieren
    db.aktualisiere_highscore("Testnutzer", 100, "Python")
    db.aktualisiere_highscore("Testnutzer", 150)
    
    # Test: Spaced Repetition
    db.aktualisiere_spaced_repetition("Testnutzer", 1, True)
    db.aktualisiere_spaced_repetition("Testnutzer", 1, True)
    db.aktualisiere_spaced_repetition("Testnutzer", 1, False)
    
    print("Datenbank-Test abgeschlossen!")
    print("Highscores:", db.get_highscores())
    print("Spaced Repetition für Frage 1:", db.get_spaced_repetition_daten("Testnutzer", 1))
