#!/usr/bin/env python3
"""HYDRA v2 - Self-Evolving AI System"""
import sys
import json
from brain import Brain
from agents import SecurityAgent

class Hydra:
    def __init__(self):
        self.brain = Brain()
        self.agents = {
            "security": SecurityAgent(self.brain),
        }
    
    def route(self, task):
        t = task.lower()
        if any(w in t for w in ["hunt", "scan", "vuln", "bug", "security"]):
            return "security"
        return "security"  # default for now
    
    def run(self, task):
        agent_name = self.route(task)
        agent = self.agents[agent_name]
        print(f"[HYDRA] → {agent_name.upper()}")
        return agent.run(task)
    
    def status(self):
        return self.brain.stats()

def main():
    h = Hydra()
    
    if len(sys.argv) < 2:
        print("HYDRA v2")
        print("  python hydra.py hunt <target>")
        print("  python hydra.py status")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        print(json.dumps(h.status(), indent=2))
    elif cmd == "hunt" and len(sys.argv) > 2:
        result = h.run(f"hunt {sys.argv[2]}")
        print(json.dumps(result, indent=2))
        # Save findings
        from config import FINDINGS_PATH
        FINDINGS_PATH.write_text(json.dumps(result, indent=2))
    else:
        result = h.run(" ".join(sys.argv[1:]))
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()