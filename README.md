
# ISIN-Handelbarkeit-Checker (comdirect)

Lokale Web-App (FastAPI) zum wöchentlichen Check via Excel-Upload, ob ISINs (Spalte B) auf Ihren Ziel-Handelsplätzen
**handelbar** sind bzw. **einen Geldkurs (Bid)** stellen. Verwahrart aus Spalte F ("Clearstream Lux.", "Clearstream Nat.", "International") steuert die Zielmärkte.

**Kursquelle:** Öffentliche Wertpapier-Seiten von comdirect (z. B. `/inf/aktien/{ISIN}`, `/inf/etfs/{ISIN}`, `/inf/fonds/{ISIN}`, `/inf/anleihen/{ISIN}`).

## Start
```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scriptsctivate
pip install -r requirements.txt
# Nur wenn HTML dynamisch ist / Blockaden auftreten:
python -m playwright install chromium
uvicorn app.main:app --reload --port 8000
```
Browser: http://localhost:8000

## Excel-Format
- **Spalte B**: ISIN
- **Spalte F**: Verwahrart (Clearstream Lux. | Clearstream Nat. | International)

## Logik
- Pro ISIN werden comdirect-Detailseiten (Aktie/ETF/Fonds/Anleihe) probiert.
- Aus "Handelsplätze" (inkl. LiveTrading) werden Marktname + Geld/Brief/ Zeit gelesen.
- Je Verwahrart gelten in `app/mapping.py` gepflegte Zielmärkte. Ist **mind. ein Bid** verfügbar, gilt die ISIN als **handelbar**.

## Anpassungen
- `app/mapping.py`: Handelsplatz-Synonyme/Listen anpassen.
- `app/scraper.py`: Zeitschranken/Parallelität (`MAX_CONCURRENCY`, `REQUEST_TIMEOUT`).

## Hinweis
- Die comdirect-REST-API stellt **keine Kursendpunkte** bereit – es wird **kein offizielles API** genutzt. Bitte Nutzungsbedingungen beachten.
