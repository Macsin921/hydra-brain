import requests
import sqlite3
import time
from datetime import datetime
from brain import get_oi_signal
from signal_utils import log_signal
from config import TG_BOT_TOKEN as BOT_TOKEN, TG_CHAT_ID as CHAT_ID

def send_tg(msg):
    try:
        requests.post("https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage", json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})
    except: pass

def get_price(ticker):
    try:
        conn = sqlite3.connect("history.db")
        cur = conn.cursor()
        cur.execute("SELECT close FROM prices WHERE ticker=? ORDER BY date DESC LIMIT 1", (ticker,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else 0
    except:
        return 0

def check_signals():
    alerts = []
    for ticker in ["SBER", "GAZP", "LKOH", "VTBR", "GMKN", "TATN"]:
        signal, reason = get_oi_signal(ticker)
        price = get_price(ticker)
        if signal == "SELL":
            alerts.append({"ticker": ticker, "signal": signal, "reason": reason, "price": price})
            log_signal("oi_monitor", ticker, "SELL", reason, "2.0")
        elif signal == "BUY":
            alerts.append({"ticker": ticker, "signal": signal, "reason": reason, "price": price})
            log_signal("oi_monitor", ticker, "BUY", reason, "2.0")
    return alerts

def main():
    print("OI Monitor v2 started")
    send_tg("OI Monitor v2 started")
    last_alerts = set()
    while True:
        try:
            alerts = check_signals()
            for a in alerts:
                key = a["ticker"] + a["signal"]
                if key not in last_alerts:
                    msg = "<b>" + a["ticker"] + "</b> " + a["signal"] + ": " + a["reason"]
                    send_tg(msg)
                    last_alerts.add(key)
                    print(a["ticker"] + " " + a["signal"] + " logged for learning")
            if len(last_alerts) > 50:
                last_alerts.clear()
            time.sleep(300)
        except Exception as e:
            print("Error: " + str(e))
            time.sleep(60)

if __name__ == "__main__":
    main()
