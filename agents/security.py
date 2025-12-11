"""Security Agent - Bug Hunting"""
import requests
import re
from .base import Agent

class SecurityAgent(Agent):
    name = "security"
    
    PATHS = ["/.env", "/.git/HEAD", "/robots.txt", "/api", "/admin", "/swagger.json", "/graphql"]
    
    def execute(self, task):
        target = task.split()[-1]
        return self.scan(target)
    
    def scan(self, target):
        findings = []
        base = f"https://{target}" if not target.startswith("http") else target
        
        # 1. Main page
        try:
            r = requests.get(base, timeout=10)
            findings.append({"type": "INFO", "url": base, "status": r.status_code})
            
            # Check headers
            headers = r.headers
            if "X-Frame-Options" not in headers:
                findings.append({"type": "MEDIUM", "vuln": "Missing X-Frame-Options"})
            if "Content-Security-Policy" not in headers:
                findings.append({"type": "LOW", "vuln": "Missing CSP"})
        except Exception as e:
            findings.append({"type": "ERROR", "error": str(e)})
            return findings
        
        # 2. Path discovery
        for p in self.PATHS:
            try:
                r = requests.get(f"{base}{p}", timeout=5, allow_redirects=False)
                if r.status_code == 200:
                    findings.append({"type": "FOUND", "url": f"{base}{p}", "size": len(r.text)})
                elif r.status_code in [301, 302, 403]:
                    findings.append({"type": "INTERESTING", "url": f"{base}{p}", "status": r.status_code})
            except:
                pass
        
        # 3. Extract links
        try:
            links = re.findall(r'href="([^"]*)"', r.text)[:20]
            for link in links:
                if "?" in link:
                    findings.append({"type": "PARAM_URL", "url": link})
        except:
            pass
        
        return findings
    
    def evaluate(self, result):
        high = sum(1 for f in result if f.get("type") in ["HIGH", "FOUND"])
        med = sum(1 for f in result if f.get("type") == "MEDIUM")
        return min(1.0, 0.2 + high * 0.2 + med * 0.1)