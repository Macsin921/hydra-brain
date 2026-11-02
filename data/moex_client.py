import requests
from datetime import datetime, timedelta


class MoexClient:
    STOCK_URL = "https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json"
    HISTORY_URL = "https://iss.moex.com/iss/history/engines/stock/markets/shares/securities/{ticker}.json"

    def get_quote(self, ticker: str) -> dict:
        try:
            r = requests.get(self.STOCK_URL.format(ticker=ticker), timeout=10)
            r.raise_for_status()
            payload = r.json()
            columns = payload["marketdata"]["columns"]
            rows = payload["marketdata"]["data"]
            if not rows:
                return {"ticker": ticker, "price": None, "change_pct": None}
            row = rows[0]

            def field(name):
                return row[columns.index(name)] if name in columns else None

            return {
                "ticker": ticker,
                "price": field("LAST"),
                "change_pct": field("LASTTOPREVPRICE"),
            }
        except Exception as exc:
            return {"ticker": ticker, "price": None, "change_pct": None, "error": str(exc)}

    def get_history(self, ticker: str, days: int = 30) -> list[dict]:
        end = datetime.now().date()
        start = end - timedelta(days=days + 10)
        try:
            r = requests.get(
                self.HISTORY_URL.format(ticker=ticker),
                params={"from": start.isoformat(), "till": end.isoformat()},
                timeout=15,
            )
            r.raise_for_status()
            payload = r.json()
            columns = payload["history"]["columns"]
            rows = payload["history"]["data"]
            result = []
            for row in rows:
                item = dict(zip(columns, row))
                if item.get("CLOSE") is not None:
                    result.append(
                        {
                            "ticker": ticker,
                            "date": item.get("TRADEDATE"),
                            "close": item.get("CLOSE"),
                            "volume": item.get("VOLUME") or 0,
                        }
                    )
            return result
        except Exception:
            return []
