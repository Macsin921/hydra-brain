#!/usr/bin/env python3
"""Диагностика MOEX FUTOI.

Проверяет:
- доступность API;
- реальные поля ответа;
- автоподбор фьючерса;
- наличие OI, изменения OI и позиций long/short.

Не отправляет Telegram и не пишет в Supabase.
"""
import json
import sys
from datetime import date

import requests

FUTOI_LIST_URL = "https://iss.moex.com/iss/analyticalproducts/futoi/securities.json"
FUTOI_SECURITY_URL = "https://iss.moex.com/iss/analyticalproducts/futoi/securities/{security}.json"


def fetch_json(url: str):
    response = requests.get(url, timeout=20)
    print(f"HTTP {response.status_code}: {url}")
    response.raise_for_status()
    return response.json()


def inspect_payload(payload: dict):
    print("\nВерхние ключи ответа:", list(payload.keys()))
    block = payload.get("futoi")
    if not isinstance(block, dict):
        print("Блок futoi отсутствует или имеет неожиданный тип:", type(block).__name__)
        return None
    print("Ключи блока futoi:", list(block.keys()))
    columns = block.get("columns") or []
    rows = block.get("data") or []
    print(f"Колонок: {len(columns)}; строк: {len(rows)}")
    print("Колонки:", columns)
    if rows:
        print("Первая строка:", rows[0])
    return {"columns": columns, "rows": rows}


def find_candidates(payload: dict, ticker: str):
    block = payload.get("futoi") or {}
    columns = block.get("columns") or []
    rows = block.get("data") or []
    candidates = []
    for row in rows:
        item = dict(zip(columns, row))
        security = str(item.get("SECID") or "")
        underlying = str(item.get("UNDERLYING") or "")
        if underlying.upper() == ticker.upper():
            candidates.append(item)
    return candidates


def main():
    ticker = sys.argv[1].upper() if len(sys.argv) > 1 else "SBER"
    print(f"Диагностика FUTOI для базового актива: {ticker}")

    try:
        list_payload = fetch_json(FUTOI_LIST_URL)
    except Exception as exc:
        print(f"ОШИБКА запроса списка FUTOI: {exc}")
        return 1

    block = inspect_payload(list_payload)
    if not block:
        return 1

    columns = block["columns"]
    rows = block["rows"]
    required = ["SECID", "UNDERLYING", "OI", "OI_CHANGE", "POS_LONG", "POS_SHORT", "EXPIRATION_DATE"]
    missing = [field for field in required if field not in columns]
    print("\nОтсутствующие ожидаемые поля:", missing or "нет")

    candidates = []
    for row in rows:
        item = dict(zip(columns, row))
        if str(item.get("UNDERLYING") or "").upper() == ticker:
            candidates.append(item)

    print(f"\nНайдено контрактов для {ticker}: {len(candidates)}")
    if not candidates:
        print("Автоподбор невозможен: ни один контракт не сопоставлен с активом.")
        return 1

    today = date.today().isoformat()
    active = []
    for item in candidates:
        expiration = str(item.get("EXPIRATION_DATE") or "")
        if expiration >= today:
            active.append(item)

    print("Активных контрактов:", len(active))
    if not active:
        print("Активных контрактов нет; выбирать истёкший контракт нельзя.")
        return 1

    best = max(active, key=lambda item: item.get("OI") or 0)
    security = best.get("SECID")
    print("Выбранный контракт по максимальному OI:", security)
    print("Данные контракта:", json.dumps(best, ensure_ascii=False, indent=2))

    try:
        security_payload = fetch_json(FUTOI_SECURITY_URL.format(security=security))
    except Exception as exc:
        print(f"ОШИБКА запроса контракта {security}: {exc}")
        return 1

    inspect_payload(security_payload)
    print("\nДиагностика завершена. Ничего в Supabase не записано, Telegram не использовался.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
