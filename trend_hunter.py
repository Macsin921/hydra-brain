import sqlite3
from datetime import datetime, timedelta
from position_sizer import TIER1, TIER2, TIER3

def get_ma(ticker, days=10):
    try:
        conn = sqlite3.connect("history.db")
        rows = conn.execute("SELECT close FROM prices WHERE ticker=? ORDER BY date DESC LIMIT ?", (ticker, days)).fetchall()
        conn.close()
        if len(rows) < days: return None
        return round(sum(r[0] for r in rows) / len(rows), 2)
    except: return None

def get_stop_loss(ticker):
    if ticker in TIER1: return -3.0
    if ticker in TIER2: return -5.0
    return -7.0  # TIER3

def should_hold(ticker, entry_price, current_price, days_held):
    ma10 = get_ma(ticker, 10)
    if not ma10: return False, "нет MA10"
    profit_pct = (current_price - entry_price) / entry_price * 100
    stop = get_stop_loss(ticker)
    if profit_pct < stop: return False, "стоп " + str(stop) + "%"
    if current_price > ma10 and profit_pct > 0: return True, "тренд ОК"
    if current_price < ma10 and days_held > 3: return False, "тренд сломан"
    return True, "наблюдаем"

def open_position(ticker, price, quantity, position_pct, reason):
    conn = sqlite3.connect("knowledge.db")
    conn.execute("INSERT INTO positions (ticker, entry_date, entry_price, quantity, position_pct, reason, status) VALUES (?,?,?,?,?,?,?)", (ticker, datetime.now().isoformat(), price, quantity, position_pct, reason, "open"))
    conn.commit()
    conn.close()

def close_position(ticker, price, reason):
    conn = sqlite3.connect("knowledge.db")
    pos = conn.execute("SELECT id, entry_price FROM positions WHERE ticker=? AND status=? LIMIT 1", (ticker, "open")).fetchone()
    if pos:
        profit = (price - pos[1]) / pos[1] * 100
        conn.execute("UPDATE positions SET status=?, exit_date=?, exit_price=?, profit_pct=? WHERE id=?", ("closed", datetime.now().isoformat(), price, round(profit, 2), pos[0]))
        conn.commit()
    conn.close()

def get_open_positions():
    conn = sqlite3.connect("knowledge.db")
    rows = conn.execute("SELECT ticker, entry_date, entry_price, position_pct FROM positions WHERE status=?", ("open",)).fetchall()
    conn.close()
    return [{"ticker": r[0], "date": r[1], "price": r[2], "pct": r[3]} for r in rows]
