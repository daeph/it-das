import PySimpleGUI as sg
import random
import json
import os
from datetime import datetime

# Pfade für Daten
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VOKABELN_DATEI = os.path.join(SCRIPT_DIR, "vokabeln.json")
ERGEBNISSE_DATEI = os.path.join(SCRIPT_DIR, "ergebnisse.json")

# Standard-Vokabeln (falls Datei nicht existiert)
standard_vokabeln = {
    "Fachbegriffe": [
        {
            "frage": "Was ist SQL?",
            "antwort": "Structured Query Language – eine Sprache für Datenbankabfragen.",
            "falsche_antworten": [
                "Ein Betriebssystem für Server.",
                "Eine Programmiersprache für Web-Apps.",
                "Ein Protokoll für Netzwerkkommunikation."
            ],
            "kategorie": "Datenbanken",
            "schwierigkeit": "⭐⭐⭐⭐⭐"
        }
    ]
}

def lade_vokabeln():
    try:
        with open(VOKABELN_DATEI, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(VOKABELN_DATEI, "w", encoding="utf-8") as f:
            json.dump(standard_vokabeln, f, indent=4, ensure_ascii=False)
        return standard_vokabeln

def speichere_vokabeln(vokabeln):
    with open(VOKABELN_DATEI, "w", encoding="utf-8") as f:
        json.dump(vokabeln, f, indent=4, ensure_ascii=False)

def lade_ergebnisse():
    try:
        with open(ERGEBNISSE_DATEI, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"statistiken": [], "highscore": 0}

def speichere_ergebnisse(ergebnisse):
    with open(ERGEBNISSE_DATEI, "w", encoding="utf-8") as f:
        json.dump(ergebnisse, f, indent=4, ensure_ascii=False)

class VokabelApp:
    def __init__(self):
        self.vokabeln = lade_vokabeln()
        self.ergebnisse = lade_ergebnisse()
        self.aktuelle_vokabel = None
        self.punkte = 0
        self.fragen_anzahl = 0
        self.highscore = self.ergebnisse.get("highscore", 0)
        self.aktuelle_kategorie = "Alle"
        self.ausgewählte_antwort = None
        sg.theme("DarkAmber")
        self.window = self.erstelle_hauptfenster()
        self.neue_frage()

    def erstelle_hauptfenster(self):
        radio_buttons = [
            [sg.Radio("", key=f"-ANTWORT_{i}-", group_id="antworten", enable_events=True,
                      font=("Arial", 12), size=(40, 1))
             for i in range(4)]
        ]
        layout = [
            [sg.Text("IT-DAS 🎯", font=("Arial", 20), justification="center")],
            [sg.HorizontalSeparator()],
            [sg.Text("", size=(40, 2), key="-FRAGE-", font=("Arial", 14), justification="center")],
            [sg.Text("", key="-KATEGORIE-", font=("Arial", 10), text_color="grey")],
            [sg.Column(radio_buttons, key="-ANTWORTEN-")],
            [
                sg.Button("Antwort prüfen", key="-PRUEFEN-", button_color=("white", "#4CAF50"), disabled=True),
                sg.Button("Neue Frage", key="-NEUE_FRAGE-", button_color=("white", "#2196F3")),
                sg.Button("Beenden", key="-BEENDEN-", button_color=("white", "#f44336"))
            ],
            [sg.Text("", key="-ERGEBNIS-", font=("Arial", 12), text_color="white")],
            [sg.Text(f"Punkte: {self.punkte}/{self.fragen_anzahl}", key="-PUNKTE-", font=("Arial", 12))],
            [sg.Text(f"Highscore: {self.highscore}", key="-HIGHSCORE-", font=("Arial", 12))]
        ]
        return sg.Window("IT-DAS", layout, finalize=True)

    def neue_frage(self):
        if not self.vokabeln["Fachbegriffe"]:
            sg.popup_error("Keine Vokabeln vorhanden!")
            return
        if self.aktuelle_kategorie == "Alle":
            gefilterte_vokabeln = self.vokabeln["Fachbegriffe"]
        else:
            gefilterte_vokabeln = [v for v in self.vokabeln["Fachbegriffe"] if v["kategorie"] == self.aktuelle_kategorie]
        if not gefilterte_vokabeln:
            sg.popup_error(f"Keine Vokabeln in der Kategorie '{self.aktuelle_kategorie}'!")
            return
        self.aktuelle_vokabel = random.choice(gefilterte_vokabeln)
        self.window["-FRAGE-"].update(self.aktuelle_vokabel["frage"])
        self.window["-KATEGORIE-"].update(f"Kategorie: {self.aktuelle_vokabel['kategorie']} | Schwierigkeit: {self.aktuelle_vokabel['schwierigkeit']}")
        alle_antworten = [self.aktuelle_vokabel["antwort"]] + self.aktuelle_vokabel["falsche_antworten"]
        random.shuffle(alle_antworten)
        for i, antwort in enumerate(alle_antworten):
            self.window[f"-ANTWORT_{i}-"].update(antwort)
        self.window["-PRUEFEN-"].update(disabled=False)
        self.window["-ERGEBNIS-"].update("")
        self.ausgewählte_antwort = None

    def ueberpruefen(self):
        if self.aktuelle_vokabel is None:
            return
        for i in range(4):
            if self.window[f"-ANTWORT_{i}-"].get():
                self.ausgewählte_antwort = self.window[f"-ANTWORT_{i}-"].DisplayText
                break
        if not self.ausgewählte_antwort:
            sg.popup_error("Bitte wähle eine Antwort aus!")
            return
        self.fragen_anzahl += 1
        korrekt = self.ausgewählte_antwort == self.aktuelle_vokabel["antwort"]
        if korrekt:
            self.punkte += 1
            self.window["-ERGEBNIS-"].update("✅ Richtig! 🎉", text_color="green")
            if self.punkte > self.highscore:
                self.highscore = self.punkte
                self.ergebnisse["highscore"] = self.highscore
                speichere_ergebnisse(self.ergebnisse)
        else:
            self.window["-ERGEBNIS-"].update(f"❌ Falsch! Richtig: {self.aktuelle_vokabel['antwort']}", text_color="red")
        self.window["-PUNKTE-"].update(f"Punkte: {self.punkte}/{self.fragen_anzahl}")
        self.window["-HIGHSCORE-"].update(f"Highscore: {self.highscore}")
        self.ergebnisse["statistiken"].append({
            "datum": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "frage": self.aktuelle_vokabel["frage"],
            "richtig": korrekt,
            "kategorie": self.aktuelle_vokabel["kategorie"],
            "ausgewählte_antwort": self.ausgewählte_antwort
        })
        speichere_ergebnisse(self.ergebnisse)
        self.window["-PRUEFEN-"].update(disabled=True)

    def run(self):
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED or event == "-BEENDEN-":
                break
            elif event == "-PRUEFEN-":
                self.ueberpruefen()
            elif event == "-NEUE_FRAGE-":
                self.neue_frage()
            elif any(values.get(f"-ANTWORT_{i}-") for i in range(4)):
                self.window["-PRUEFEN-"].update(disabled=False)
        self.window.close()

if __name__ == "__main__":
    app = VokabelApp()
    app.run()