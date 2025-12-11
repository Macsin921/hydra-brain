"""HYDRA Configuration"""
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "brain.db"
FINDINGS_PATH = BASE_DIR / "findings.json"

# Telegram (optional)
TG_TOKEN = None
TG_CHAT = None

# Timeouts
REQUEST_TIMEOUT = 10
SCAN_THREADS = 5