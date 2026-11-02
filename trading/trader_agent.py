import os
import requests


class TraderAgent:
    def __init__(self):
        self.api_key = os.getenv("API_KEY", "")
        self.api_url = os.getenv("API_URL", "https://openrouter.ai/api/v1/chat/completions")
        self.model = os.getenv("MODEL", "deepseek/deepseek-chat")
        self.tg_token = os.getenv("TG_BOT_TOKEN", "")
        self.tg_chat_id = os.getenv("TG_CHAT_ID", "")

    def explain(self, signal: dict) -> str:
        if not self.api_key:
            return "LLM не настроена: объяснение недоступно."
        facts = "\n".join(f"- {key}: {value}" for key, value in signal.items())
        try:
            response = requests.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Ты аналитик MOEX. Не выдумывай сигналы. Кратко объясни уже рассчитанный сигнал на основе данных. Максимум 3 предложения.",
                        },
                        {"role": "user", "content": facts},
                    ],
                    "max_tokens": 180,
                },
                timeout=30,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            return f"Ошибка LLM: {exc}"

    def send_telegram(self, text: str) -> bool:
        if not self.tg_token or not self.tg_chat_id:
            return False
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{self.tg_token}/sendMessage",
                json={"chat_id": self.tg_chat_id, "text": text},
                timeout=15,
            )
            return response.ok
        except Exception:
            return False
