#!/usr/bin/env python3
"""
PUMP DETECTOR v1.0
Формула: Volume_spike + OI_spike + Delta_positive = ПАМП
"""

import sqlite3
from datetime import datetime

HISTORY_DB = "history.db"
KNOWLEDGE_DB = "knowledge.db"

# ВСЕ 52 ТИКЕРА
TICKERS = [
    'AFKS','AFLT','ALRS','BELU','BSPB','CBOM','CHMF','CNRU','FEES','GAZP',
    'GMKN','HEAD','HYDR','IRAO','LEAS','LKOH','MAGN','MGNT','MOEX','MTLR',
    'MTSS','NLMK','NVTK','OZON','PHOR','PIKK','PLZL','POLY','POSI','RNFT',
    'ROSN','RTKM','RUAL','SBER','SBERP','SFIN','SGZH','SIBN','SMLT','SNGS',
    'SNGSP','SPBE','SVAV','SVCB','T','TATN','TATNP','TRNFP','VKCO','VTBR',
    'X5','YDEX'
]

# Пороги
VOLUME_SPIKE = 2.0      # объём > 2x от среднего
OI_SPIKE = 10.0         # OI вырос > 10%
DELTA_STRONG = 20.0     # дельта > 20% от объёма

def get_volume_ratio(ticker):
    """Отношение текущего объёма к среднему за 20 дней"""
    conn = sqlite3.connect(HISTORY_DB)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT volume FROM prices 
        WHERE ticker=? ORDER BY date DESC LIMIT 1
    """, (ticker,))
    row = cur.fetchone()
    if not row: return 0, 0, 0
    vol_now = row[0]
    
    cur.execute("""
        SELECT AVG(volume) FROM (
            SELECT volume FROM prices 
            WHERE ticker=? ORDER BY date DESC LIMIT 20
        )
    """, (ticker,))
    vol_avg = cur.fetchone()[0] or 1
    conn.close()
    
    return vol_now, int(vol_avg), round(vol_now / vol_avg, 2)

def get_oi_change(ticker):
    """Изменение OI за день"""
    conn = sqlite3.connect(HISTORY_DB)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT oi, oi_change FROM futures_oi 
        WHERE ticker LIKE ? ORDER BY date DESC LIMIT 1
    """, (ticker + '%',))
    row = cur.fetchone()
    conn.close()
    
    if not row: return 0, 0, 0
    oi, oi_change = row
    oi_prev = oi - oi_change if oi_change else oi
    oi_pct = round((oi_change / oi_prev * 100), 2) if oi_prev else 0
    
    return oi, oi_prev, oi_pct

def get_delta(ticker):
    """Дельта покупки-продажи (из futoi если есть)"""
    conn = sqlite3.connect(HISTORY_DB)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT pos_long, pos_short FROM futoi 
        WHERE ticker LIKE ? ORDER BY date DESC LIMIT 1
    """, (ticker + '%',))
    row = cur.fetchone()
    conn.close()
    
    if not row: return 0, 0
    longs, shorts = row
    delta = longs - shorts
    total = longs + shorts
    delta_pct = round((delta / total * 100), 2) if total else 0
    
    return delta, delta_pct

def calc_pump_score(vol_ratio, oi_pct, delta_pct):
    """Считаем общий скор пампа (0-100)"""
    score = 0
    
    # Volume component (max 33)
    if vol_ratio >= VOLUME_SPIKE:
        score += min(33, (vol_ratio - 1) * 10)
    
    # OI component (max 33)
    if oi_pct >= OI_SPIKE:
        score += min(33, oi_pct / 2)
    
    # Delta component (max 34)
    if delta_pct >= DELTA_STRONG:
        score += min(34, delta_pct)
    
    return round(score, 1)

def detect_pump(ticker):
    """Проверяем тикер на памп"""
    vol, vol_avg, vol_ratio = get_volume_ratio(ticker)
    oi, oi_prev, oi_pct = get_oi_change(ticker)
    delta, delta_pct = get_delta(ticker)
    
    score = calc_pump_score(vol_ratio, oi_pct, delta_pct)
    
    return {
        'ticker': ticker,
        'volume': vol,
        'volume_avg': vol_avg,
        'volume_ratio': vol_ratio,
        'oi': oi,
        'oi_change_pct': oi_pct,
        'delta': delta,
        'delta_pct': delta_pct,
        'pump_score': score,
        'is_pump': score >= 50
    }

def save_pump_signal(data):
    """Сохраняем в БД"""
    if data['pump_score'] < 30:
        return
    
    conn = sqlite3.connect(KNOWLEDGE_DB)
    conn.execute("""
        INSERT INTO pump_signals 
        (dt, ticker, volume, volume_avg, volume_ratio, 
         oi, oi_prev, oi_change_pct, delta, delta_pct, pump_score)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        datetime.now().isoformat(),
        data['ticker'],
        data['volume'],
        data['volume_avg'],
        data['volume_ratio'],
        data['oi'],
        data.get('oi_prev', 0),
        data['oi_change_pct'],
        data['delta'],
        data['delta_pct'],
        data['pump_score']
    ))
    conn.commit()
    conn.close()

def scan_all():
    """Сканируем все тикеры"""
    pumps = []
    for t in TICKERS:
        r = detect_pump(t)
        if r['pump_score'] >= 30:
            pumps.append(r)
            save_pump_signal(r)
            print(f"{'🚀' if r['is_pump'] else '⚡'} {t}: score={r['pump_score']}")
            print(f"   vol={r['volume_ratio']}x oi={r['oi_change_pct']}% delta={r['delta_pct']}%")
    
    return pumps

if __name__ == "__main__":
    print("=" * 50)
    print(f"PUMP DETECTOR: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)
    print(f"Тикеров: {len(TICKERS)}")
    print(f"Пороги: vol>{VOLUME_SPIKE}x, oi>{OI_SPIKE}%, delta>{DELTA_STRONG}%")
    print("-" * 50)
    
    pumps = scan_all()
    
    print("-" * 50)
    if pumps:
        print(f"Найдено сигналов: {len(pumps)}")
        top = max(pumps, key=lambda x: x['pump_score'])
        print(f"ТОП: {top['ticker']} score={top['pump_score']}")
    else:
        print("Пампов не обнаружено")
