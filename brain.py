"""HYDRA Brain - Memory System"""
import sqlite3
import json
from datetime import datetime
from config import DB_PATH

class Brain:
    def __init__(self):
        self.db = sqlite3.connect(DB_PATH)
        self._init()
    
    def _init(self):
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                agent TEXT,
                task TEXT,
                result TEXT,
                score REAL,
                ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY,
                key TEXT UNIQUE,
                value TEXT,
                updated TIMESTAMP
            );
        """)
        self.db.commit()
    
    def save_task(self, agent, task, result, score=0.5):
        self.db.execute(
            "INSERT INTO tasks (agent, task, result, score) VALUES (?,?,?,?)",
            (agent, task, json.dumps(result), score)
        )
        self.db.commit()
    
    def get_history(self, agent=None, limit=10):
        if agent:
            rows = self.db.execute(
                "SELECT task, result, score FROM tasks WHERE agent=? ORDER BY ts DESC LIMIT ?",
                (agent, limit)
            ).fetchall()
        else:
            rows = self.db.execute(
                "SELECT agent, task, score FROM tasks ORDER BY ts DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return rows
    
    def remember(self, key, value):
        self.db.execute(
            "INSERT OR REPLACE INTO knowledge (key, value, updated) VALUES (?,?,?)",
            (key, json.dumps(value), datetime.now().isoformat())
        )
        self.db.commit()
    
    def recall(self, key):
        row = self.db.execute("SELECT value FROM knowledge WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else None
    
    def stats(self):
        rows = self.db.execute("""
            SELECT agent, COUNT(*), ROUND(AVG(score), 2) 
            FROM tasks GROUP BY agent
        """).fetchall()
        return {r[0]: {"tasks": r[1], "avg_score": r[2]} for r in rows}