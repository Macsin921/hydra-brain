from dataclasses import dataclass, asdict
from tickers import tier_of


@dataclass
class Signal:
    ticker: str
    direction: str
    score: float
    price: float | None
    reasons: list[str]
    tier: int


class SignalEngine:
    VOLUME_SPIKE = 2.0
    OI_SPIKE = 10.0
    DELTA_STRONG = 20.0
    PUMP_THRESHOLD = 50.0

    def moving_average(self, closes: list[float], period: int = 10) -> float | None:
        if len(closes) < period:
            return None
        return round(sum(closes[-period:]) / period, 2)

    def stop_loss_pct(self, ticker: str) -> float:
        return {-1: -3.0, 1: -3.0, 2: -5.0}.get(tier_of(ticker), -7.0)

    def build_signal(
        self,
        ticker: str,
        price: float | None,
        closes: list[float],
        volume_ratio: float = 0.0,
        oi_change_pct: float = 0.0,
        delta_pct: float = 0.0,
    ) -> Signal:
        reasons = []
        score = 0.0

        if volume_ratio >= self.VOLUME_SPIKE:
            points = min(33.0, (volume_ratio - 1) * 10)
            score += points
            reasons.append(f"Объём {volume_ratio:.2f}x от среднего")

        if oi_change_pct >= self.OI_SPIKE:
            points = min(33.0, oi_change_pct / 2)
            score += points
            reasons.append(f"OI вырос на {oi_change_pct:.2f}%")

        if delta_pct >= self.DELTA_STRONG:
            points = min(34.0, delta_pct)
            score += points
            reasons.append(f"Дельта long/short {delta_pct:.2f}%")

        ma10 = self.moving_average(closes)
        if price and ma10:
            if price > ma10:
                reasons.append(f"Цена выше MA10 ({ma10})")
            else:
                reasons.append(f"Цена ниже MA10 ({ma10})")

        if score >= self.PUMP_THRESHOLD:
            direction = "WATCH_LONG"
        elif price and ma10 and price < ma10:
            direction = "WATCH_SHORT"
        else:
            direction = "NEUTRAL"

        return Signal(
            ticker=ticker,
            direction=direction,
            score=round(score, 1),
            price=price,
            reasons=reasons,
            tier=tier_of(ticker),
        )

    def to_dict(self, signal: Signal) -> dict:
        return asdict(signal)
