import os
import requests
from datetime import datetime, timezone


class SupabaseClient:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL", "").rstrip("/")
        self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    @property
    def enabled(self) -> bool:
        return bool(self.url and self.key)

    def _headers(self):
        return {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }

    def insert(self, table: str, row: dict) -> bool:
        if not self.enabled:
            return False
        try:
            response = requests.post(
                f"{self.url}/rest/v1/{table}",
                headers=self._headers(),
                json=row,
                timeout=15,
            )
            return response.ok
        except Exception:
            return False

    def save_snapshot(self, data: dict, ma10: float | None) -> bool:
        return self.insert(
            "market_snapshots",
            {
                "ticker": data["ticker"],
                "price": data.get("price"),
                "volume_ratio": data.get("volume_ratio"),
                "oi_change_pct": data.get("oi_change_pct"),
                "delta_pct": data.get("delta_pct"),
                "ma10": ma10,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    def save_signal(self, signal: dict) -> bool:
        return self.insert(
            "signals",
            {
                "ticker": signal["ticker"],
                "direction": signal["direction"],
                "score": signal["score"],
                "price": signal.get("price"),
                "reasons": signal.get("reasons", []),
                "source": "hydra",
                "status": "new",
            },
        )
