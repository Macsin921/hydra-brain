import sqlite3
import numpy as np
import requests
import os

class EpisoddicMemory:
    def __init__(self, db_path="episodes.db"):
        self.db = sqlite3.connect(db_path)
        self.$HF_TOKEN = os.environ.get("HF_TOKEN")
        self.api_url = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"
        self._load_index()
    
    def _load_index(self):
        rows = self.db.execute(
            "SELECT id, embedding FROM episodes WHERE embedding IS NOT NULL"
        ).fetchall()
        self.ids = []
        vectors = []
        for eid, blob in rows:
            emb = np.frombuffer(blob, dtype=np.float32)
            if len(emb) == 384:
                self.ids.append(eid)
                vectors.append(emb)
        if vectors:
            self.matrix = np.vstack(vectors)
            norms = np.linalg.norm(self.matrix, axis=1, keepdims=True)
            self.matrix_norm = self.matrix / norms
        else:
            self.matrix_norm = None
        print(f"[MEM] Loaded {len(self.ids)} vectors")
    
    def _embed(self, text):
        if not self.$HF_TOKEN:
            return None
        headers = {"Authorization": f"Bearer {self.$HF_TOKEN}"}
        r = requests.post(self.api_url, headers=headers, json={"inputs": text}, timeout=15)
        if r.status_code == 200:
            return np.array(r.json(), dtype=np.float32)
        return None
    
    def search(self, query, k=5):
        """Семантический поиск похожих эпизодов"""
        if self.matrix_norm is None or len(self.ids) == 0:
            return []
        q_emb = self._embed(query)
        if q_emb is None:
            return []
        q_norm = q_emb / np.linalg.norm(q_emb)
        scores = self.matrix_norm @ q_norm
        top_k = np.argsort(scores)[::-1][:k]
        results = []
        for idx in top_k:
            db_id = self.ids[idx]
            row = self.db.execute(
                "SELECT task, approach, result FROM episodes WHERE id=?", (db_id,)
            ).fetchone()
            if row:
                results.append({
                    "id": db_id, "task": row[0], "approach": row[1],
                    "result": row[2], "score": float(scores[idx])
                })
        return results
    
    def add(self, task, approach, result):
        """Добавить новый эпизод"""
        emb = self._embed(task)
        blob = emb.tobytes() if emb is not None else None
        cur = self.db.execute(
            "INSERT INTO episodes (task, approach, result, embedding) VALUES (?,?,?,?)",
            (task, approach, result, blob)
        )
        self.db.commit()
        if blob:
            self._load_index()
        return cur.lastrowid
    
    def get(self, episode_id):
        """Получить эпизод по ID"""
        row = self.db.execute(
            "SELECT id, task, approach, result FROM episodes WHERE id=?", (episode_id,)
        ).fetchone()
        if row:
            return {"id": row[0], "task": row[1], "approach": row[2], "result": row[3]}
        return None
    
    def recent(self, n=10):
        """Последние n эпизодов"""
        rows = self.db.execute(
            "SELECT id, task, approach, result FROM episodes ORDER BY id DESC LIMIT ?", (n,)
        ).fetchall()
        return [{"id": r[0], "task": r[1], "approach": r[2], "result": r[3]} for r in rows]
    
    def delete(self, episode_id):
        """Удалить эпизод"""
        self.db.execute("DELETE FROM episodes WHERE id=?", (episode_id,))
        self.db.commit()
        self._load_index()
    
    def update(self, episode_id, task=None, approach=None, result=None):
        """Обновить эпизод"""
        ep = self.get(episode_id)
        if not ep:
            return False
        task = task or ep["task"]
        approach = approach or ep["approach"]
        result = result or ep["result"]
        emb = self._embed(task)
        blob = emb.tobytes() if emb is not None else None
        self.db.execute(
            "UPDATE episodes SET task=?, approach=?, result=?, embedding=? WHERE id=?",
            (task, approach, result, blob, episode_id)
        )
        self.db.commit()
        self._load_index()
        return True
    
    def stats(self):
        """Статистика базы"""
        total = self.db.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
        with_emb = self.db.execute("SELECT COUNT(*) FROM episodes WHERE embedding IS NOT NULL").fetchone()[0]
        unique_tasks = self.db.execute("SELECT COUNT(DISTINCT task) FROM episodes").fetchone()[0]
        return {"total": total, "with_embedding": with_emb, "unique_tasks": unique_tasks}
    
    # Aliases
    add_episode = add

EpisodicMemory = EpisoddicMemory
