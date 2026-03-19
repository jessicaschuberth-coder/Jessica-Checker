
import io
import asyncio
from typing import List, Dict
import pandas as pd
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from .scraper import get_markets_for_isin, MAX_CONCURRENCY
from .mapping import get_target_markets, market_matches

app = FastAPI(title='ISIN-Handelbarkeit-Checker (comdirect)')
templates = Jinja2Templates(directory='app/templates')
app.mount('/static', StaticFiles(directory='app/static'), name='static')

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

async def process_isin(isin: str, custody: str) -> Dict:
    targets = get_target_markets(custody)
    markets = await get_markets_for_isin(isin)
    # Filter: nur Zielhandelsplätze
    relevant = []
    for m in markets:
        if market_matches(targets, m.get('market','')):
            relevant.append(m)
    # Handelbar, wenn mind. ein Bid vorhanden & nicht "--"
    def has_bid(x):
        bid = (x.get('bid') or '').strip()
        return bid not in ('', '--', '-')
    is_tradable = any(has_bid(m) for m in relevant)
    return {
        'isin': isin,
        'custody': custody,
        'tradable': is_tradable,
        'matched_markets': relevant,
    }

@app.post('/check', response_class=HTMLResponse)
async def check(request: Request, file: UploadFile = File(...)):
    # Excel einlesen
    content = await file.read()
    df = pd.read_excel(io.BytesIO(content), engine='openpyxl', header=None)
    # Erwartung: Spalte B (Index 1): ISIN, Spalte F (Index 5): Verwahrart
    rows = []
    for _, row in df.iterrows():
        isin = str(row.iloc[1]).strip() if len(row) > 1 else ''
        custody = str(row.iloc[5]).strip() if len(row) > 5 else ''
        # grobe ISIN-Prüfung
        if len(isin) >= 11 and any(c.isalpha() for c in isin):
            rows.append((isin, custody))
    # Parallel abarbeiten (sanfte Begrenzung)
    sem = asyncio.Semaphore(MAX_CONCURRENCY)
    results: List[Dict] = []
    async def worker(isin, custody):
        async with sem:
            res = await process_isin(isin, custody)
            results.append(res)
    await asyncio.gather(*(worker(i,c) for i,c in rows))

    # Zusammenfassung
    tradable = sum(1 for r in results if r['tradable'])
    return templates.TemplateResponse('result.html', {
        'request': request,
        'total': len(results),
        'tradable': tradable,
        'not_tradable': len(results)-tradable,
        'results': results,
    })

@app.post('/export')
async def export(file: UploadFile = File(...)):
    content = await file.read()
    df = pd.read_excel(io.BytesIO(content), engine='openpyxl', header=None)
    rows = []
    for _, row in df.iterrows():
        isin = str(row.iloc[1]).strip() if len(row) > 1 else ''
        custody = str(row.iloc[5]).strip() if len(row) > 5 else ''
        if len(isin) >= 11 and any(c.isalpha() for c in isin):
            rows.append((isin, custody))
    sem = asyncio.Semaphore(MAX_CONCURRENCY)
    out: List[Dict] = []
    async def worker(isin, custody):
        async with sem:
            res = await process_isin(isin, custody)
            out.append(res)
    await asyncio.gather(*(worker(i,c) for i,c in rows))
    # CSV erzeugen
    import csv
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(['ISIN','Verwahrart','Handelbar','Gefundene Ziel-Handelsplätze (Bid/Ask/Zeit)'])
    for r in out:
        mk = '; '.join([f"{m.get('market')} | Bid={m.get('bid')} | Ask={m.get('ask')} | Zeit={m.get('time')}" for m in r['matched_markets']])
        w.writerow([r['isin'], r['custody'], 'Ja' if r['tradable'] else 'Nein', mk])
    data = buf.getvalue().encode('utf-8')
    return StreamingResponse(io.BytesIO(data), media_type='text/csv', headers={'Content-Disposition': 'attachment; filename="handelbarkeit.csv"'})
