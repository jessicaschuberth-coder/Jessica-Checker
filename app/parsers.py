
from bs4 import BeautifulSoup
from typing import Optional, List, Dict

def parse_instrument_type(html: str) -> Optional[str]:
    # einfache Heuristik (Titel)
    soup = BeautifulSoup(html, 'lxml')
    title = (soup.title.string or '').lower() if soup.title else ''
    if 'etf' in title:
        return 'etf'
    if 'anleihe' in title or 'bond' in title:
        return 'anleihe'
    if 'fonds' in title:
        return 'fonds'
    if 'aktie' in title:
        return 'aktie'
    return None


def extract_markets_with_quotes(html: str) -> List[Dict]:
    """Extrahiert tabellarisch aufgeführte Handelsplätze inkl. Geld/Brief/Zeit.
    Rückgabe: Liste[{ 'market','bid','ask','time' }]
    """
    soup = BeautifulSoup(html, 'lxml')
    markets: List[Dict] = []

    tables = soup.find_all('table')
    for tbl in tables:
        headers = [th.get_text(strip=True).lower() for th in tbl.find_all('th')]
        if not headers:
            continue
        if any(k in headers for k in ['handelsplatz', 'börse', 'boerse', 'markt', 'live trading', 'livetrading']):
            for tr in tbl.find_all('tr'):
                tds = tr.find_all('td')
                if not tds:
                    continue
                rowtxt = [td.get_text(strip=True) for td in tds]
                market = rowtxt[0] if rowtxt else ''
                bid = None; ask = None; zeit = None
                for j, h in enumerate(headers):
                    val = rowtxt[j] if j < len(rowtxt) else ''
                    if 'geld' in h: bid = val
                    if 'brief' in h: ask = val
                    if 'zeit' in h or 'datum' in h: zeit = val
                markets.append({'market': market, 'bid': bid, 'ask': ask, 'time': zeit})
    return markets
