#!/usr/bin/env python3
"""Telegram-интерфейс HYDRA.

Команды:
/scan [limit] - быстрый скан рынка
/top [limit] - лучшие сигналы по score
/status - статус HYDRA
/help - помощь
"""
import os
import time
import requests

from hydra import Hydra
from config import TG_BOT_TOKEN, TG_CHAT_ID

API_URL = "https://api.telegram.org/bot{token}/getUpdates"
SEND_URL = "https://api.telegram.org/bot{token}/sendMessage"


class TelegramHydraBot:
    def __init__(self):
        self.hydra = Hydra()
        self.token = TG_BOT_TOKEN
        self.chat_id = TG_CHAT_ID
        self.offset = 0

    def send(self, text: str):
        try:
            requests.post(
                SEND_URL.format(token=self.token),
                json={"chat_id": self.chat_id, "text": text[:4000]},
                timeout=15,
            )
        except Exception as exc:
            print(f"Telegram send error: {exc}")

    def handle(self, command: str, argument: str = ""):
        command = command.lower()
        if command in ["/start", "/help"]:
            return (
                "HYDRA Trading Agent\n\n"
                "/scan [limit] - скан рынка\n"
                "/top [limit] - лучшие сигналы\n"
                "/status - статус системы\n"
                "/help - помощь"
            )
        if command == "/scan":
            limit = int(argument) if argument.isdigit() else 5
            signals = self.hydra.trade_scan(limit=limit, explain=False, persist=True)
            lines = ["HYDRA scan:"]
            for item in signals:
                lines.append(
                    f"{item['ticker']} — {item['direction']} | score {item['score']} | {', '.join(item['reasons']) or 'нет причин'}"
                )
            return "\n".join(lines)
        if command == "/top":
            limit = int(argument) if argument.isdigit() else 10
            signals = self.hydra.trade_scan(limit=limit, explain=False, persist=False)
            active = [item for item in signals if item["direction"] != "NEUTRAL"]
            active.sort(key=lambda item: item["score"], reverse=True)
            if not active:
                return "Активных сигналов нет."
            lines = ["Топ сигналов:"]
            for item in active[:10]:
                lines.append(
                    f"{item['ticker']} — {item['direction']} | score {item['score']} | {', '.join(item['reasons'])}"
                )
            return "\n".join(lines)
        if command == "/status":
            return "HYDRA работает. Используй /scan или /top."
        return "Неизвестная команда. /help — список команд."

    def run(self):
        if not self.token or not self.chat_id:
            raise SystemExit("Нужны TG_BOT_TOKEN и TG_CHAT_ID")
        self.send("HYDRA Telegram-бот запущен.")
        while True:
            try:
                response = requests.get(
                    API_URL.format(token=self.token),
                    params={"offset": self.offset + 1, "timeout": 30},
                    timeout=35,
                )
                updates = response.json().get("result", [])
                for update in updates:
                    self.offset = update["update_id"]
                    message = update.get("message") or {}
                    chat_id = str(message.get("chat", {}).get("id", ""))
                    if chat_id != str(self.chat_id):
                        continue
                    text = (message.get("text") or "").strip()
                    if not text.startswith("/"):
                        continue
                    parts = text.split()
                    command = parts[0]
                    argument = parts[1] if len(parts) > 1 else ""
                    self.send(self.handle(command, argument))
            except Exception as exc:
                print(f"Bot error: {exc}")
                time.sleep(5)


if __name__ == "__main__":
    TelegramHydraBot().run()
