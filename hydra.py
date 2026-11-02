#!/usr/bin/env python3
"""HYDRA v2 - Self-Evolving AI System"""
import json
import sys

from brain import Brain
from agents import SecurityAgent
from data.moex_client import MoexClient
from trading.signal_engine import SignalEngine
from trading.trader_agent import TraderAgent
from tickers import TICKERS


class Hydra:
    def __init__(self):
        self.brain = Brain()
        self.moex = MoexClient()
        self.engine = SignalEngine()
        self.trader = TraderAgent()
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

    def trade_scan(self, limit: int = 5):
        results = []
        for ticker in TICKERS[:limit]:
            quote = self.moex.get_quote(ticker)
            history = self.moex.get_history(ticker, days=30)
            closes = [item["close"] for item in history if item.get("close")]
            signal = self.engine.build_signal(
                ticker=ticker,
                price=quote.get("price"),
                closes=closes,
            )
            results.append(self.engine.to_dict(signal))
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
        print("  python hydra.py trade scan [limit]")
        print("  python hydra.py hunt <target>")
        print("  python hydra.py status")
        return

    command = sys.argv[1]

    if command == "status":
        print(json.dumps(hydra.status(), indent=2, ensure_ascii=False))
    elif command == "trade" and len(sys.argv) > 2 and sys.argv[2] == "scan":
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        signals = hydra.trade_scan(limit)
        print(json.dumps(signals, indent=2, ensure_ascii=False))
    elif command == "hunt" and len(sys.argv) > 2:
        result = hydra.run(f"hunt {sys.argv[2]}")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        result = hydra.run(" ".join(sys.argv[1:]))
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
