# Запуск HYDRA на VPS

## 1. Клонировать проект

```bash
sudo apt update && sudo apt install -y python3 python3-pip git
sudo git clone https://github.com/Macsin921/hydra-brain.git /opt/hydra-brain
cd /opt/hydra-brain
```

## 2. Создать .env

```bash
cp .env.example .env
nano .env
```

Заполни:

```env
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
TG_BOT_TOKEN=...
TG_CHAT_ID=...
API_KEY=...
MODEL=deepseek/deepseek-chat
```

Никогда не коммить `.env` в Git.

## 3. Проверить вручную

```bash
chmod +x run.sh
./run.sh
```

Если в Telegram пришло «HYDRA Telegram-бот запущен», всё работает.

## 4. Установить автозапуск

```bash
sudo cp deploy/hydra-bot.service /etc/systemd/system/hydra-bot.service
sudo systemctl daemon-reload
sudo systemctl enable --now hydra-bot
```

## 5. Управление

```bash
sudo systemctl status hydra-bot
sudo systemctl restart hydra-bot
sudo journalctl -u hydra-bot -f
```

## 6. Обновление

```bash
cd /opt/hydra-brain
sudo git pull
sudo systemctl restart hydra-bot
```
