
# Handelsplatz-Sets gemäß Vorgabe
# - Clearstream Lux. & Clearstream Nat. -> Emittenten (LiveTrading) + deutsche Börsen
# - International -> Auslandsbörsen

CLEARSTREAM_TARGETS = {
    # LiveTrading / Emittenten (Synonyme, Kleinschreibung)
    'DEUTSCHE BANK': ['lt deutsche bank', 'deutsche bank'],
    'HSBC': ['lt hsbc', 'hsbc'],
    'LANG & SCHWARZ': ['lt lang & schwarz', 'lang & schwarz', 'l&s', 'ls exchange'],
    'SOCIETE GENERALE': ['lt societe generale', 'societe generale', 'sg'],
    'LANG & SCHWARZ EXCHANGE': ['ls exchange'],
    'CITI': ['lt citi', 'citi', 'citigroup'],
    'GOLDMAN SACHS': ['lt goldman sachs', 'goldman sachs'],
    'BONDINVEST': ['bondinvest'],
    'UBS': ['lt ubs', 'ubs'],
    'BAADER': ['lt baader trading', 'baader', 'baader trading'],
    'VONTOBEL': ['lt vontobel', 'vontobel'],
    'HVB': ['lt hvb', 'hvb', 'unicredit'],
    'ERSTE BANK': ['lt erste bank', 'erste bank'],
    'MORGAN STANLEY': ['lt morgan stanley', 'morgan stanley'],
    'DZ BANK': ['lt dz bank', 'dz bank'],
    'ING INVESTMENT': ['ing investment', 'ing'],
    'COMMERZBANK': ['lt commerzbank', 'commerzbank'],
    # Börsen DE
    'XETRA': ['xetra'],
    'BERLIN': ['berlin'],
    'DÜSSELDORF': ['düsseldorf', 'duesseldorf', 'dusseldorf'],
    'FRANKFURT': ['frankfurt'],
    'HAMBURG': ['hamburg'],
    'HANNOVER': ['hannover'],
    'STUTTGART': ['stuttgart'],
    'MÜNCHEN': ['münchen', 'muenchen', 'munich'],
    'GETTEX': ['gettex'],
    'QUOTRIX': ['quotrix'],
    'FRANKFURT ZERTIFIKATE': ['frankfurt zertifikate', 'frankfurt cert'],
    # Tradegate-Varianten
    'TRADEGATE': ['tradegate', 'tradegate bonds', 'tradegate fonds'],
}

INTERNATIONAL_TARGETS = {
    'AMSTERDAM': ['euronext amsterdam', 'amsterdam'],
    'MAILAND': ['milano', 'mailand', 'borsa italiana'],
    'NASDAQ': ['nasdaq'],
    'NYSE': ['nyse'],
    'NYSE ARCA': ['nyse arca', 'arca'],
    'AMEX': ['amex', 'nyse mkt'],
    'OTC BB': ['otc bb', 'otc bulletin board', 'otc'],
    'PARIS': ['euronext paris', 'paris'],
    'TORONTO': ['tsx', 'toronto'],
    'TSX VENTURE': ['tsx venture', 'tsxv'],
    'WIEN': ['wien', 'vienna'],
    'LISSABON': ['lissabon', 'lisbon', 'euronext lisbon'],
    'BRÜSSEL': ['brüssel', 'bruessel', 'brussels', 'euronext brussels'],
}

# Hilfsfunktionen

def get_target_markets(custody: str):
    custody = (custody or '').strip().lower()
    if custody.startswith('international'):
        return INTERNATIONAL_TARGETS
    # Default: Clearstream Lux. & Nat.
    return CLEARSTREAM_TARGETS


def normalize(s: str) -> str:
    return (s or '').strip().lower()


def market_matches(targets: dict, market_name: str) -> bool:
    n = normalize(market_name)
    for syns in targets.values():
        for syn in syns:
            if syn in n:
                return True
    return False
