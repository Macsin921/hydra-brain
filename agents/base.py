"""Base Agent Class"""
import time
from brain import Brain

class Agent:
    name = "base"
    
    def __init__(self, brain=None):
        self.brain = brain or Brain()
    
    def run(self, task):
        start = time.time()
        try:
            result = self.execute(task)
            score = self.evaluate(result)
            self.brain.save_task(self.name, task, result, score)
            return {"ok": True, "result": result, "score": score}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def execute(self, task):
        raise NotImplementedError
    
    def evaluate(self, result):
        if isinstance(result, list):
            return min(1.0, 0.3 + len(result) * 0.1)
        return 0.5