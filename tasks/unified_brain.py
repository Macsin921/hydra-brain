# -*- coding: utf-8 -*-
import os, requests

class UnifiedBrain:
    def __init__(self):
        self.hf_api = "https://diorrock-hydra-fixer.hf.space/api/predict"
        print("[BRAIN] Ready")
    
    def fix_remote(self, code):
        try:
            r = requests.post(self.hf_api, json={"data": [code]}, timeout=30)
            if r.status_code == 200: return r.json().get("data", [None])[0]
        except: pass
        return None

if __name__ == "__main__":
    b = UnifiedBrain()
    print(b.fix_remote("print 'hello' SyntaxError"))