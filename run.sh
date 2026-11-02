#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [ ! -f .env ]; then
  echo "Файл .env не найден. Скопируй .env.example в .env и заполни секреты."
  exit 1
fi

set -a
source .env
set +a

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

exec python3 telegram_bot.py
