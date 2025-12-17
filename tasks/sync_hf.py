import os, requests, json

GH_TOKEN = os.environ.get('GH_TOKEN', '')
HF_TOKEN = os.environ.get('HF_TOKEN', '')
GH_REPO = "Macsin921/hydra-brain"
HF_REPO = "hydra-fixer"

def push_to_hf(data, filename):
    """Push data to HF Space"""
    url = f"https://huggingface.co/api/spaces/{HF_REPO}/upload/{filename}"
    r = requests.put(url, headers={"Authorization": f"Bearer {HF_TOKEN}"}, json=data)
    return r.status_code

def pull_from_gh(path):
    """Pull from GitHub"""
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{path}"
    r = requests.get(url, headers={"Authorization": f"token {GH_TOKEN}"})
    if r.status_code == 200:
        import base64
        return json.loads(base64.b64decode(r.json()['content']))
    return {}

if __name__ == '__main__':
    print("=== SYNC: GitHub <-> HuggingFace ===")
    fixes = pull_from_gh("data/fix_memory.json")
    print(f"Loaded {len(fixes)} fixes from GitHub")
