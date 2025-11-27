Hier ist die vollständige Übersetzung ins Deutsche — klar, professionell und für technische Dokumentation geeignet:

---

# **Emico PDF Generator**

Ein kleines Dienstprogramm (GUI + CLI), das Emico-Produktseiten ausliest und druckbare Produktdatenblätter (PDF) generiert.

Projektbetreiber: **syskomp gehmeyr GmbH — Emico Division**
Website: [https://www.emico.com](https://www.emico.com)

---

## **Kurze Zusammenfassung**

* **Zweck:** Abrufen von Produktinformationen von Emico-Produktseiten und Zusammenstellen eines formatierten PDF-Datenblatts.
* **Modi:** GUI (`ui.py`) und Standalone/CLI (`main.py`).
* **Ausgabe:** PDF-Dateien, die in einem konfigurierbaren Ordner gespeichert werden.

---

## **Voraussetzungen**

Siehe `requirements.txt` für die im Projekt verwendeten externen Python-Pakete.

---

## **Installation**

1. **Python 3.9+ installieren** (empfohlen).
2. **Virtuelle Umgebung erstellen und aktivieren:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. **Abhängigkeiten installieren:**

```powershell
pip install -r requirements.txt
```

---

## **Verwendung**

### **GUI-Modus** (für nicht-technische Nutzer empfohlen):

```powershell
python ui.py
```

### **Standalone / CLI-Modus:**

```powershell
python main.py
```

---

## **Hinweise und Konfiguration**

* Das Projekt verwendet derzeit einen fest codierten Standard-Speicherordner
  (`G:\6Artikel\Datenblätter(Produkte)`) in `main.py` und `ui.py`, falls kein Ordner angegeben wird.
  Es wird empfohlen, dies vor einer Veröffentlichung anzupassen (Umgebungsvariable, CLI-Argument oder z. B. `Path.home()/"Downloads"`).

* Beispieländerung:
  Nutzung einer Umgebungsvariable **`EMICO_PDF_OUTPUT`** oder Hinzufügen einer CLI-Option **`--output`**.

---

## **Daten-Dateien und Build-Artefakte**

* Dieses Repository enthält Beispiel-Excel-Dateien (`Mappe1.xlsx`, `Importvorlage_aktuell.xlsx`).
  Diese Dateien können umgebungsspezifische Pfade und/oder Firmendaten enthalten.

* Empfehlung:
  Keine Rohdaten oder Build-Artefakte einchecken.
  Halten Sie `build/` und `.xlsx`-Dateien außerhalb des Repos oder fügen Sie nur bereinigte Beispiele hinzu.

---

## **Rechtlicher Hinweis / Scraping**

* Das Tool ruft Inhalte von **emico.com** ab, um Datenblätter zu erstellen.
  Bitte sicherstellen, dass Scraping und automatisierte Anfragen mit den Nutzungsbedingungen und der `robots.txt` von Emico übereinstimmen.
  Für kommerzielle Nutzung oder Massendownloads sollte dies mit dem Emico-Team bzw. der Rechtsabteilung abgestimmt werden, um Rate-Limits oder Richtlinienverstöße zu vermeiden.

---

## **Empfohlene Änderungen für modulareren Code**

* Trennung der Verantwortlichkeiten in Module:

  * `scraper.py`: gesamte Web-Scraping- und Parsing-Logik (momentan in `main.py`).
  * `pdf.py`: PDF-Erzeugungslogik (aktuell `pdf_generator.py`) — kann beibehalten, sollte aber eine klar definierte öffentliche API bereitstellen.
  * `cli.py`: CLI-Argumentverarbeitung und Einstiegspunkt.
  * `gui.py`: UI-Code (bereits `ui.py`) — UI-Logik getrennt halten und nur öffentliche APIs aus Scraper/PDF-Modulen verwenden.

* **Vorteile:**
  bessere Testbarkeit, klarere Struktur, geringerer Änderungsaufwand, bessere Wiederverwendbarkeit.

---

## **Erstellen einer ausführbaren Anwendung**

Um eine ausführbare Datei zu erzeugen, folgenden Befehl im Terminal ausführen:
(Der Name `"PDF-Generator_v1.2"` kann frei angepasst werden.)

```
pyinstaller --onefile --noconsole -clean --name "PDF-Generator_v1.2" --icon "assets/emicologo.ico" --add-data "assets:assets" ui.py
```

---

## **Kontakt**

Bei Fragen zu Inhalt oder Lizenzierung: **[sales@emico.com](mailto:sales@emico.com)**
oder den Repository-Verantwortlichen innerhalb der syskomp-Gruppe kontaktieren.

---

Wenn du möchtest, kann ich die deutsche Version auch **formatieren**, **kürzen**, **für ein Readme.md optimieren**, **in offiziellerer Sprache**, oder als **Vorlage für Confluence** aufbereiten.
