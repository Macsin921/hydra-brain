import requests

def get_stock_data(ticker):
    try:
        url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json"
        r = requests.get(url, timeout=10)
        data = r.json()
        md = data["marketdata"]["data"]
        if md and len(md) > 0:
            cols = data["marketdata"]["columns"]
            row = md[0]
            get = lambda n: row[cols.index(n)] if n in cols else None
            return {"price": get("LAST"), "change": get("LASTTOPREVPRICE")}
    except:
        pass
    return {"price": None, "change": None}

def get_commodity(code):
    try:
        if code in ["USD", "EUR", "CNY"]:
            r = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=10)
            d = r.json()["Valute"][code]
            return {"price": d["Value"], "change": round((d["Value"] - d["Previous"]) / d["Previous"] * 100, 2)}
        if code == "GOLD":
            r = requests.get("https://iss.moex.com/iss/engines/currency/markets/selt/boards/CETS/securities/GLDRUB_TOM.json", timeout=10)
            md = r.json()["marketdata"]["data"]
            if md and md[0]:
                cols = r.json()["marketdata"]["columns"]
                return {"price": md[0][cols.index("LAST")] if "LAST" in cols else None, "change": None}
        if code == "RGBI":
            r = requests.get("https://iss.moex.com/iss/engines/stock/markets/index/boards/RTSI/securities/RGBI.json", timeout=10)
            md = r.json()["marketdata"]["data"]
            if md and md[0]:
                cols = r.json()["marketdata"]["columns"]
                last = md[0][cols.index("CURRENTVALUE")] if "CURRENTVALUE" in cols else 0
                return {"price": last, "change": 0}
    except:
        pass
    return {"price": None, "change": None}

def get_price(ticker):
    data = get_stock_data(ticker)
    return data.get("price")

def get_trend(ticker, days=5):
    try:
        from datetime import datetime, timedelta
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=days+5)).strftime("%Y-%m-%d")
        url = f"https://iss.moex.com/iss/history/engines/stock/markets/shares/securities/{ticker}.json?from={start}&till={end}"
        r = requests.get(url, timeout=10)
        data = r.json()["history"]["data"]
        if len(data) < 2: return None
        prices = [row[11] for row in data if row[11]]
        if len(prices) < 2: return None
        old = prices[-days-1] if len(prices) > days else prices[0]
        return round((prices[-1] - old) / old * 100, 2)
    except: return None

def get_dividends(ticker):
    try:
        r = requests.get(f"https://iss.moex.com/iss/securities/{ticker}/dividends.json", timeout=10)
        data = r.json()["dividends"]["data"]
        cols = r.json()["dividends"]["columns"]
        return [{"date": row[cols.index("registryclosedate")], "value": row[cols.index("value")]} for row in data if row[cols.index("registryclosedate")]]
    except: return []
