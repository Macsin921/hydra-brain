import requests
from datetime import date


FUTOI_URL = "https://iss.moex.com/iss/analyticalproducts/futoi/securities.json"


def nearest_future_for(ticker: str) -> str | None:
    """Ищет ближайший ликвидный фьючерс на базовый актив.
    Использует FUTOI и выбирает инструмент с максимальным открытым интересом.
    """
    try:
        response = requests.get(FUTOI_URL, timeout=15)
        response.raise_for_status()
        payload = response.json()
        columns = payload["futoi"]["columns"]
        rows = payload["futoi"]["data"]
        candidates = []
        for row in rows:
            item = dict(zip(columns, row))
            security = item.get("SECID") or ""
            underlying = item.get("UNDERLYING") or ""
            if underlying.upper() != ticker.upper():
                continue
            candidates.append(
                {
                    "security": security,
                    "oi": item.get("OI") or 0,
                    "expiration": item.get("EXPIRATION_DATE") or "",
                }
            )
        if not candidates:
            return None
        today = date.today().isoformat()
        active = [item for item in candidates if item["expiration"] >= today]
        pool = active or candidates
        best = max(pool, key=lambda item: item["oi"])
        return best["security"]
    except Exception:
        return None
