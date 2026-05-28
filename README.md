# IT-DAS Vokabeltrainer 🎯

**Ein kostenloser Multiple-Choice-Vokabeltest für IT-Begriffe mit Spaced Repetition System**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PySimpleGUI](https://img.shields.io/badge/PySimpleGUI-4.60.5-green.svg)](https://www.pysimplegui.org/)

---

## 📚 Über IT-DAS

IT-DAS (IT-Dein Abfragesystem) ist ein **kostenloser, Open-Source Vokabeltrainer** speziell für IT-Begriffe. Die App hilft dir, dein Wissen in verschiedenen IT-Bereichen spielerisch zu verbessern und langfristig zu behalten.

### ✨ Hauptmerkmale

- 🎯 **Multiple-Choice-Quiz** mit Fragen zu Programmiersprachen, Informatik-Abkürzungen, Mathematik und mehr
- 📁 **Mehrfachauswahl bei Kategorien** - Wähle mehrere Kategorien gleichzeitig
- ✅ **Mehrfachantworten möglich** - Einige Fragen haben mehrere richtige Antworten
- 🔄 **Spaced Repetition System** - Intelligente Wiederholungslogik für langfristiges Lernen
- 🏆 **Highscore-System** - Verfolge deinen Fortschritt und vergleiche dich mit anderen
- 👤 **Nutzerverwaltung** - Speichere deinen Fortschritt unter deinem Nutzernamen
- 🎨 **Cyberpunk-Design** - Matrix-Regen-Effekt im Hintergrund mit grünem Farbschema
- 📱 **Responsive Layout** - Funktioniert auf PC und (eingeschränkt) auf mobilen Geräten
- 💰 **100% kostenlos & Open-Source** - Keine In-App-Käufe, keine Werbung

---

## 🚀 Schnellstart

### Voraussetzungen

- Python 3.8 oder höher
- pip (Python Paketmanager)

### Installation

1. **Repository klonen:**
   ```bash
   git clone https://github.com/daeph/it-das.git
   cd it-das
   ```

2. **Abhängigkeiten installieren:**
   ```bash
   pip install -r src/requirements.txt
   ```

3. **App starten:**
   ```bash
   python src/main.py
   ```

---

## 📂 Projektstruktur

```
it-das/
├── src/
│   ├── main.py          # Hauptanwendung (GUI + Quiz-Logik)
│   ├── vokabeln.json    # Fragenpool mit allen Kategorien
│   ├── database.py      # Nutzerdaten, Highscores, Spaced Repetition
│   └── requirements.txt # Python-Abhängigkeiten
├── README.md            # Diese Datei
└── LICENSE              # MIT-Lizenz
```

---

## 🎯 Unterstützte Kategorien

### Programmiersprachen
- Python, Java, C++, JavaScript, C#, PHP, Ruby, Go, Rust, Swift, Kotlin, TypeScript

### Informatik-Abkürzungen
- API, CPU, RAM, GPU, OS, HTTP, HTTPS, URL, IP, DNS, TCP, UDP, SQL, NoSQL, etc.

### Mathematische Sprache
- Algorithmen, Big-O-Notation, Rekursion, Graphen, Matrizen, Sortieralgorithmen, etc.

### Sonstiges
- Datenbanken (MySQL, PostgreSQL, MongoDB, etc.)
- Netzwerke (Protokolle, OSI-Modell, etc.)
- Betriebssysteme (Linux, Windows, macOS, etc.)
- DevOps (Docker, Git, CI/CD, etc.)
- Cloud (AWS, Azure, Google Cloud, etc.)
- Sicherheit (Verschlüsselung, Authentifizierung, etc.)
- Datenstrukturen (Stack, Queue, Hash-Tabelle, etc.)
- Webentwicklung (HTML, CSS, REST, etc.)
- Versionierung (Git, SVN, etc.)

---

## 🔧 Spaced Repetition System

IT-DAS verwendet ein **intelligentes Wiederholungssystem**, um dein Lernen zu optimieren:

| Richtige Antworten in Folge | Nächste Wiederholung |
|-----------------------------|---------------------|
| 1. richtige Antwort         | nach 3 Tagen        |
| 2. richtige Antwort         | nach 5 Tagen        |
| 3. richtige Antwort         | nach 7 Tagen        |
| 4+ richtige Antworten       | nach 30 Tagen       |

**Bei falscher Antwort:** Sofortige Wiederholung in der gleichen Session

---

## 📊 Punktevergabe

- **Vollständig richtig:** Alle richtigen Antworten ausgewählt, keine falschen → Volle Punktzahl
- **Teilweise richtig:** Einige richtige Antworten ausgewählt → Teilpunkte
- **Falsch:** Falsche Antworten ausgewählt oder richtige nicht → 0 Punkte

---

## 🎨 Design & UI

- **Matrix-Regen-Effekt:** Durchgehende Animation im Hintergrund (25% langsamer als Standard)
- **Cyberpunk-Style:** Grüne Schrift (#00ff00) auf dunklem Hintergrund (#0a0a0a)
- **Gleichmäßige Transparenz:** Alle UI-Elemente haben eine konsistente Transparenz
- **Responsive:** Passt sich verschiedenen Bildschirmgrößen an

---

## 📝 Fragenpool erweitern

Du kannst den Fragenpool einfach erweitern, indem du die Datei `src/vokabeln.json` bearbeitest.

### Format einer Frage:

```json
{
  "id": 31,
  "frage": "Was ist die Hauptfunktion einer Firewall?",
  "kategorien": ["Sicherheit", "Netzwerke"],
  "antworten": ["Schutz vor unerwünschtem Netzwerkverkehr", "Filterung von Datenpaketen"],
  "falsche_antworten": [
    "Erhöhung der Internetgeschwindigkeit",
    "Speicherung von Passwörtern",
    "Verschlüsselung von E-Mails",
    "Verwaltung von Benutzerkonten"
  ],
  "erklärung": "Eine Firewall dient primär dem Schutz vor unerwünschtem Netzwerkverkehr und der Filterung von Datenpaketen.",
  "schwierigkeit": "⭐⭐",
  "mehrfachantwort": true
}
```

### Felder:
- `id`: Eindeutige Identifikationsnummer
- `frage`: Der Fragetext
- `kategorien`: Liste der Kategorien, zu denen die Frage gehört
- `antworten`: Liste der richtigen Antworten (kann mehrere enthalten)
- `falsche_antworten`: Liste der falschen Antwortmöglichkeiten
- `erklärung`: Optionale Erklärung der richtigen Antwort
- `schwierigkeit`: Schwierigkeitsgrad (⭐ bis ⭐⭐⭐⭐⭐)
- `mehrfachantwort`: Boolean - ob mehrere Antworten richtig sein können

---

## 💾 Datenbank

IT-DAS speichert folgende Daten lokal:

1. **nutzer_daten.json** - Nutzerprofile und Statistiken
2. **highscore.json** - Highscore-Listen (global und pro Kategorie)
3. **spaced_repetition.json** - Spaced Repetition Daten für jeden Nutzer

Alle Daten werden im `src/` Verzeichnis gespeichert.

---

## 🤝 Mitwirken

Beiträge sind herzlich willkommen! Hier sind einige Möglichkeiten, wie du helfen kannst:

1. **Neue Fragen hinzufügen:** Erweitere den Fragenpool in `vokabeln.json`
2. **Fehler melden:** Erstelle ein Issue auf GitHub
3. **Code verbessern:** Pull Requests sind willkommen
4. **Dokumentation verbessern:** Hilf bei der Dokumentation
5. **Übersetzungen:** Hilf bei Übersetzungen in andere Sprachen

### Beitragsrichtlinien:
- Folge dem bestehenden Code-Stil
- Füge Tests für neue Funktionen hinzu
- Aktualisiere die Dokumentation
- Halte Commit-Messages klar und präzise

---

## 📜 Lizenz

IT-DAS wird unter der **MIT-Lizenz** veröffentlicht. Siehe [LICENSE](LICENSE) für Details.

---

## 🙏 Spenden

IT-DAS ist 100% kostenlos und Open-Source. Wenn du das Projekt unterstützen möchtest, kannst du:

- **PayPal:** [Spenden-Link einfügen]
- **GitHub Sponsors:** [GitHub Sponsors-Link einfügen]
- **Ko-fi:** [Ko-fi-Link einfügen]

Jede Spende hilft bei der Weiterentwicklung und Wartung des Projekts!

---

## 📞 Kontakt

- **GitHub:** [https://github.com/daeph/it-das](https://github.com/daeph/it-das)
- **Issues:** [https://github.com/daeph/it-das/issues](https://github.com/daeph/it-das/issues)
- **Pull Requests:** [https://github.com/daeph/it-das/pulls](https://github.com/daeph/it-das/pulls)

---

## 🎉 Danke!

Vielen Dank, dass du IT-DAS verwendest! Wir hoffen, dass dir die App beim Lernen von IT-Begriffen hilft. 😊

**Happy Learning!** 🚀
