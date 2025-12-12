#!/usr/bin/env python3
"""Trader Agent v2 - GitHub compatible"""
import os
import sys
import json
import requests
from datetime import datetime

# Config from env
API_KEY = os.getenv("API_KEY", "")
API_URL = os.getenv("API_URL", "https://openrouter.ai/api/v1/chat/completions")
MODEL = os.getenv("MODEL", "deepseek/deepseek-chat")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
TG_CHAT_ID = os.getenv("TG_CHAT_ID", "")

TICKERS = ["SBER", "GAZP", "LKOH", "SFIN", "MTLR", "OZON", "YNDX", "TCSG"]

class AITrader:
    def __init__(self):
        self.api_key = API_KEY
        self.api_url = API_URL
    
    def get_signal(self, ticker):
        """Получает сигнал от LLM"""
        try:
            r = requests.post(self.api_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": "Ты трейдинг аналитик MOEX. Отвечай кратко: BUY/SELL/HOLD и уверенность 0-1"},
                        {"role": "user", "content": f"Анализ {ticker} на сегодня. Формат: SIGNAL confidence"}
                    ],
                    "max_tokens": 50
                }, timeout=30)
            return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"ERROR: {e}"
    
    def scan(self):
        """Сканирует тикеры"""
        signals = []
        for t in TICKERS[:5]:  # Лимит для GitHub
            sig = self.get_signal(t)
            print(f"{t}: {sig}")
            signals.append({"ticker": t, "signal": sig})
        return signals
    
    def alert(self):
        """Отправляет алерты в TG"""
        signals = self.scan()
        
        # Фильтруем BUY
        buys = [s for s in signals if "BUY" in s["signal"].upper()]
        
        if buys:
            msg = f"📈 MOEX Signals {datetime.now().strftime('%d.%m %H:%M')}

"
            for s in buys:
                msg += f"• {s['ticker']}: {s['signal']}
"
            
            requests.post(
                f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
                json={"chat_id": TG_CHAT_ID, "text": msg}
            )
            print(f"Sent {len(buys)} alerts")
        else:
            print("No BUY signals")
            # Отправляем статус
            requests.post(
                f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
                json={"chat_id": TG_CHAT_ID, "text": f"🔍 Scan complete: no signals {datetime.now().strftime('%H:%M')}"}
            )

if __name__ == "__main__":
    trader = AITrader()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    
    if cmd == "scan":
        trader.scan()
    elif cmd == "alert":
        trader.alert()
