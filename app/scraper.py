
from typing import Optional, Tuple, List, Dict
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from .parsers import extract_markets_with_quotes

BASES = [
    'https://www.comdirect.de/inf/aktien/{isin}',
    'https://www.comdirect.de/inf/etfs/{isin}',
    'https://www.comdirect.de/inf/fonds/{isin}',
    'https://www.comdirect.de/inf/anleihen/{isin}',
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36',
    'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
}

REQUEST_TIMEOUT = 20
MAX_CONCURRENCY = 5

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=4))
async def fetch(client: httpx.AsyncClient, url: str) -> Tuple[int, str]:
    r = await client.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, follow_redirects=True)
    return r.status_code, r.text

async def fetch_instrument_html(isin: str) -> Optional[str]:
    async with httpx.AsyncClient() as client:
        for tmpl in BASES:
            url = tmpl.format(isin=isin)
            try:
                status, html = await fetch(client, url)
                if status == 200 and ('comdirect' in html.lower()):
                    return html
            except Exception:
                continue
    return None

async def fetch_with_playwright(isin: str) -> Optional[str]:
    try:
        from playwright.async_api import async_playwright
    except Exception:
        return None
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(user_agent=HEADERS['User-Agent'], locale='de-DE')
        page = await context.new_page()
        for tmpl in BASES:
            url = tmpl.format(isin=isin)
            try:
                await page.goto(url, timeout=REQUEST_TIMEOUT*1000)
                await page.wait_for_timeout(1000)
                html = await page.content()
                if 'comdirect' in html.lower():
                    await browser.close()
                    return html
            except Exception:
                continue
        await browser.close()
        return None

async def get_markets_for_isin(isin: str) -> List[Dict]:
    html = await fetch_instrument_html(isin)
    if not html:
        html = await fetch_with_playwright(isin)
    if not html:
        return []
    return extract_markets_with_quotes(html)
