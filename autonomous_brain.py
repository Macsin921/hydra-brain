"""
Автономный торговый мозг
Сам учится, сам торгует, сам улучшается
"""
import os
import json
import requests
from datetime import datetime

class AutonomousBrain:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.api_url = os.getenv("API_URL")
        self.tg_token = os.getenv("TG_BOT_TOKEN")
        self.tg_chat = os.getenv("TG_CHAT_ID")
        self.memory_file = "brain_memory.json"
        self.load_memory()
    
    def load_memory(self):
        try:
            with open(self.memory_file) as f:
                self.memory = json.load(f)
        except:
            self.memory = {"trades": [], "accuracy": 0, "lessons": []}
    
    def save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=2)
    
    def think(self, context):
        """Думает через LLM"""
        r = requests.post(self.api_url, 
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": os.getenv("MODEL", "deepseek/deepseek-chat"),
                "messages": [
                    {"role": "system", "content": f"""Ты автономный торговый агент.
Твоя память: {json.dumps(self.memory['lessons'][-5:], ensure_ascii=False)}
Твоя точность: {self.memory['accuracy']}%
Анализируй и учись на ошибках."""},
                    {"role": "user", "content": context}
                ]
            })
        return r.json()["choices"][0]["message"]["content"]
    
    def learn(self, trade_result):
        """Учится на результате"""
        lesson = self.think(f"Сделка: {trade_result}. Какой урок извлечь?")
        self.memory["lessons"].append({
            "date": str(datetime.now()),
            "trade": trade_result,
            "lesson": lesson
        })
        self.save_memory()
        return lesson
    
    def alert(self, msg):
        """Отправка в TG"""
        requests.post(
            f"https://api.telegram.org/bot{self.tg_token}/sendMessage",
            json={"chat_id": self.tg_chat, "text": f"🧠 Brain: {msg}"}
        )
    
    def run_cycle(self):
        """Один цикл работы"""
        # 1. Анализ рынка
        analysis = self.think("Проанализируй текущую ситуацию на MOEX. Дай 1-2 идеи.")
        
        # 2. Отправка
        self.alert(analysis[:500])
        
        # 3. Сохранение
        self.memory["trades"].append({
            "date": str(datetime.now()),
            "analysis": analysis
        })
        self.save_memory()
        
        return analysis

if __name__ == "__main__":
    brain = AutonomousBrain()
    result = brain.run_cycle()
    print(result)
