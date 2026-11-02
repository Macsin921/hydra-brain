#!/usr/bin/env python3
"""HYDRA v2 - Self-Evolving AI System"""
import json
import sys

from brain import Brain
from agents import SecurityAgent
from data.moex_client import MoexClient
from data.supabase_client import SupabaseClient
from trading.market_features import MarketFeatures
from trading.signal_engine import SignalEngine
from trading.trader_agent import TraderAgent
from tickers import TICKERS


class Hydra:
    def __init__(self):
        self.brain = Brain()
        self.moex = MoexClient()
        self.features = MarketFeatures(self.moex)
        self.engine = SignalEngine()
        self.trader = TraderAgent()
        self.db = SupabaseClient()
        self.agents = {
            "security": SecurityAgent(self.brain),
        }

    def route(self, task: str) -> str:
        task = task.lower()
        if any(word in task for word in ["trade", "signal", "pump", "moex", "ticker"]):
            return "trade"
        if any(word in task for word in ["hunt", "scan", "vuln", "bug", "security"]):
            return "security"
        return "security"

    def trade_scan(self, limit: int = 5, explain: bool = False, persist: bool = True):
        results = []
        for ticker in TICKERS[:limit]:
            data = self.features.collect(ticker)
            signal = self.engine.build_signal(
                ticker=ticker,
                price=data["price"],
                closes=data["closes"],
                volume_ratio=data["volume_ratio"],
                oi_change_pct=data["oi_change_pct"],
                delta_pct=data["delta_pct"],
            )
            item = self.engine.to_dict(signal)
            ma10 = self.engine.moving_average(data["closes"])

            if persist:
                item["saved_snapshot"] = self.db.save_snapshot(data, ma10)
                if item["direction"] != "NEUTRAL":
                    item["saved_signal"] = self.db.save_signal(item)

            if explain and item["direction"] != "NEUTRAL":
                item["explanation"] = self.trader.explain(item)

            results.append(item)
        return results

    def run(self, task: str):
        agent_name = self.route(task)
        if agent_name == "trade":
            return self.trade_scan()
        agent = self.agents[agent_name]
        return agent.run(task)

    def status(self):
        return self.brain.stats()


def main():
    hydra = Hydra()

    if len(sys.argv) < 2:
        print("HYDRA v2")
        print("  python hydra.py trade scan [limit] [--explain] [--no-save]")
        print("  python hydra.py hunt <target>")
        print("  python hydra.py status")
        return

    command = sys.argv[1]

    if command == "status":
        print(json.dumps(hydra.status(), indent=2, ensure_ascii=False))
    elif command == "trade" and len(sys.argv) > 2 and sys.argv[2] == "scan":
        args = sys.argv[3:]
        explain = "--explain" in args
        persist = "--no-save" not in args
        numeric = [int(value) for value in args if value.isdigit()]
        limit = numeric[0] if numeric else 5
        signals = hydra.trade_scan(limit, explain, persist)
        print(json.dumps(signals, indent=2, ensure_ascii=False))
    elif command == "hunt" and len(sys.argv) > 2:
        result = hydra.run(f"hunt {sys.argv[2]}")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        result = hydra.run(" ".join(sys.argv[1:]))
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
