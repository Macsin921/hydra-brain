"""
Graph Memory - Ассоциативная память с распространением активации
"""
import sqlite3
import numpy as np
import requests
import os
from collections import defaultdict

class GraphMemory:
    def __init__(self, db_path="graph_memory.db"):
        self.db = sqlite3.connect(db_path)
        self.$HF_TOKEN = os.environ.get("HF_TOKEN")
        self.api_url = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"
        self._init_db()
        
    def _init_db(self):
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY, concept TEXT UNIQUE,
                embedding BLOB, activation REAL DEFAULT 0, access_count INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS edges (
                src INTEGER, dst INTEGER, weight REAL DEFAULT 1.0, co_occur INTEGER DEFAULT 1,
                PRIMARY KEY (src, dst)
            );
            CREATE INDEX IF NOT EXISTS idx_concept ON nodes(concept);
        """)
        self.db.commit()
    
    def _embed(self, text):
        if not self.$HF_TOKEN:
            return None
        try:
            r = requests.post(self.api_url, headers={"Authorization": f"Bearer {self.$HF_TOKEN}"}, json={"inputs": text}, timeout=15)
            if r.status_code == 200:
                return np.array(r.json(), dtype=np.float32)
        except: pass
        return None
    
    def _get_or_create_node(self, concept):
        concept = concept.lower().strip()
        row = self.db.execute("SELECT id FROM nodes WHERE concept=?", (concept,)).fetchone()
        if row: return row[0]
        emb = self._embed(concept)
        blob = emb.tobytes() if emb is not None else None
        cur = self.db.execute("INSERT INTO nodes (concept, embedding) VALUES (?,?)", (concept, blob))
        self.db.commit()
        return cur.lastrowid
    
    def link(self, a, b, weight=1.0):
        id_a, id_b = self._get_or_create_node(a), self._get_or_create_node(b)
        for src, dst in [(id_a, id_b), (id_b, id_a)]:
            self.db.execute("""INSERT INTO edges (src, dst, weight, co_occur) VALUES (?,?,?,1)
                ON CONFLICT(src, dst) DO UPDATE SET weight = weight + ?, co_occur = co_occur + 1
            """, (src, dst, weight, weight * 0.1))
        self.db.commit()
    
    def strengthen(self, concepts):
        for i, a in enumerate(concepts):
            for b in concepts[i+1:]:
                self.link(a, b, weight=0.5)
    
    def spread(self, query, depth=3, decay=0.7):
        self.db.execute("UPDATE nodes SET activation = 0")
        q_emb = self._embed(query)
        if q_emb is None: return []
        rows = self.db.execute("SELECT id, concept, embedding FROM nodes WHERE embedding IS NOT NULL").fetchall()
        if not rows: return []
        q_norm = q_emb / np.linalg.norm(q_emb)
        activations = {}
        for nid, concept, blob in rows:
            emb = np.frombuffer(blob, dtype=np.float32)
            if len(emb) == 384:
                sim = float(np.dot(emb / np.linalg.norm(emb), q_norm))
                if sim > 0.3: activations[nid] = sim
        for _ in range(depth):
            new_act = defaultdict(float)
            for nid, act in activations.items():
                for dst, weight in self.db.execute("SELECT dst, weight FROM edges WHERE src=?", (nid,)).fetchall():
                    new_act[dst] += act * weight * decay
            for nid, act in new_act.items():
                activations[nid] = max(activations.get(nid, 0), act)
        results = []
        for nid, act in sorted(activations.items(), key=lambda x: -x[1])[:10]:
            concept = self.db.execute("SELECT concept FROM nodes WHERE id=?", (nid,)).fetchone()[0]
            self.db.execute("UPDATE nodes SET activation=?, access_count=access_count+1 WHERE id=?", (act, nid))
            results.append({"concept": concept, "activation": round(act, 3)})
        self.db.commit()
        return results
    
    def path(self, a, b, max_depth=5):
        id_a = self.db.execute("SELECT id FROM nodes WHERE concept=?", (a.lower(),)).fetchone()
        id_b = self.db.execute("SELECT id FROM nodes WHERE concept=?", (b.lower(),)).fetchone()
        if not id_a or not id_b: return None
        id_a, id_b = id_a[0], id_b[0]
        visited = {id_a: [a.lower()]}
        queue = [id_a]
        for _ in range(max_depth):
            if not queue: break
            new_queue = []
            for nid in queue:
                for (dst,) in self.db.execute("SELECT dst FROM edges WHERE src=?", (nid,)).fetchall():
                    if dst == id_b:
                        return visited[nid] + [self.db.execute("SELECT concept FROM nodes WHERE id=?", (dst,)).fetchone()[0]]
                    if dst not in visited:
                        visited[dst] = visited[nid] + [self.db.execute("SELECT concept FROM nodes WHERE id=?", (dst,)).fetchone()[0]]
                        new_queue.append(dst)
            queue = new_queue
        return None
    
    def stats(self):
        return {
            "nodes": self.db.execute("SELECT COUNT(*) FROM nodes").fetchone()[0],
            "edges": self.db.execute("SELECT COUNT(*) FROM edges").fetchone()[0],
            "with_embedding": self.db.execute("SELECT COUNT(*) FROM nodes WHERE embedding IS NOT NULL").fetchone()[0]
        }
    
    def visualize(self, limit=20):
        edges = self.db.execute("""SELECT n1.concept, n2.concept, e.weight FROM edges e
            JOIN nodes n1 ON e.src=n1.id JOIN nodes n2 ON e.dst=n2.id
            WHERE e.src < e.dst ORDER BY e.weight DESC LIMIT ?""", (limit,)).fetchall()
        lines = []
        for a, b, w in edges:
            bar = "=" * min(int(w * 5), 20)
            lines.append(f"{a[:15]:15} {bar}> {b[:15]}")
        return chr(10).join(lines)