import requests
from data.moex_client import MoexClient


class MarketFeatures:
    FUTOI_URL = "https://iss.moex.com/iss/analyticalproducts/futoi/securities/{security}.json"

    def __init__(self, moex_client: MoexClient):
        self.moex = moex_client

    def volume_ratio(self, history: list[dict]) -> float:
        volumes = [item.get("volume") or 0 for item in history if item.get("volume")]
        if len(volumes) < 21 or not volumes[-1]:
            return 0.0
        current = volumes[-1]
        average = sum(volumes[-21:-1]) / 20
        return round(current / average, 2) if average else 0.0

    def futoi(self, ticker: str) -> dict:
        """Пробует получить OI и позиции из MOEX FUTOI.
        Для акций нужен соответствующий тикер фьючерса; если данных нет, возвращает нули."""
        try:
            response = requests.get(self.FUTOI_URL.format(security=ticker), timeout=10)
            response.raise_for_status()
            payload = response.json()
            columns = payload["futoi"]["columns"]
            rows = payload["futoi"]["data"]
            if not rows:
                return {"oi_change_pct": 0.0, "delta_pct": 0.0}
            row = dict(zip(columns, rows[-1]))
            oi = row.get("OI") or 0
            oi_change = row.get("OI_CHANGE") or 0
            longs = row.get("POS_LONG") or 0
            shorts = row.get("POS_SHORT") or 0
            oi_prev = oi - oi_change
            oi_change_pct = round(oi_change / oi_prev * 100, 2) if oi_prev else 0.0
            total = longs + shorts
            delta_pct = round((longs - shorts) / total * 100, 2) if total else 0.0
            return {"oi_change_pct": oi_change_pct, "delta_pct": delta_pct}
        except Exception:
            return {"oi_change_pct": 0.0, "delta_pct": 0.0}

    def collect(self, ticker: str) -> dict:
        history = self.moex.get_history(ticker, days=30)
        closes = [item["close"] for item in history if item.get("close")]
        quote = self.moex.get_quote(ticker)
        features = self.futoi(ticker)
        return {
            "ticker": ticker,
            "price": quote.get("price"),
            "closes": closes,
            "volume_ratio": self.volume_ratio(history),
            "oi_change_pct": features["oi_change_pct"],
            "delta_pct": features["delta_pct"],
        }
