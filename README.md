# Emico PDF Generator

A small utility (GUI + CLI) that scrapes Emico product pages and generates printable product datasheets (PDF).

Project maintained by: syskomp gehmeyr GmbH — Emico Division
Website: https://www.emico.com

Quick summary
- Purpose: Fetch product information from Emico product pages and compile it into a formatted PDF datasheet.
- Modes: GUI (`ui.py`) and standalone/CLI (`main.py`).
- Output: PDF files saved to a configurable folder.

Requirements
See `requirements.txt` for the external Python packages used by the project.

Installation
1. Install Python 3.9+ (recommended).
2. Create a virtual environment and activate it:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

Usage
- GUI mode (recommended for non-technical users):

```powershell
python ui.py
```

- Standalone / CLI mode:

```powershell
python main.py
```

Notes and configuration
- The project currently uses a fallback hardcoded save folder (`G:\6Artikel\Datenblätter(Produkte)`) in `main.py` and `ui.py` when a folder is not provided. It's recommended to change this to a configurable path (environment variable, CLI argument, or `Path.home()/"Downloads"`) before publishing.
- Example change: use an environment variable `EMICO_PDF_OUTPUT` or add a `--output` CLI option.

Data files and build artifacts
- This repository contains example Excel files (`Mappe1.xlsx`, `Importvorlage_aktuell.xlsx`). These files may contain environment-specific paths and/or company data.
- We recommend not committing raw data or build artifacts. Keep `build/` and `.xlsx` files out of the repo or add sanitized examples only.

Legal / scraping note
- The tool scrapes emico.com to assemble datasheets. Make sure scraping and automated requests comply with Emico's terms of use and robots.txt. For commercial or bulk usage, coordinate with the Emico team / legal to avoid rate-limiting or policy violations.

Making the code more modular (recommended changes)
- Separate concerns into modules:
  - `scraper.py`: all web-scraping and parsing logic (currently in `main.py`).
  - `pdf.py`: PDF generation logic (currently `pdf_generator.py`) — can be kept but refactored to expose a small public API.
  - `cli.py`: CLI argument handling and entrypoint.
  - `gui.py`: UI code (already `ui.py`) — keep UI logic separate and only call public APIs from scraper/pdf modules.
- Benefits: easier testing, clearer boundaries, smaller surface for changes, better reuse.

When you want a executable application, execute the following command in terminal. You can replace the name "PDF-Generator_v1.2" with the name you like.
pyinstaller --onefile --noconsole -clean --name "PDF-Generator_v1.2" --icon "assets/emicologo.ico" --add-data "assets:assets" ui.py
 
Contact
For questions about content or licensing, contact `sales@emico.com` or the repository owner in the syskomp group.

---

Generated: 2025-11-27

