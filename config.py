import os

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
TG_CHAT_ID = os.getenv("TG_CHAT_ID", "")
API_KEY = os.getenv("API_KEY", "")
API_URL = os.getenv("API_URL", "https://openrouter.ai/api/v1/chat/completions")
MODEL = os.getenv("MODEL", "deepseek/deepseek-chat")

TICKERS = [
    "SBER", "GAZP", "LKOH", "ROSN", "NVTK",
    "GMKN", "YNDX", "MTSS", "MGNT", "POLY",
    "CHMF", "NLMK", "ALRS", "MOEX", "TATN",
    "SNGS", "VTBR", "PHOR", "RUAL", "PLZL",
    "AFLT", "PIKK", "IRAO", "FEES", "HYDR",
    "SFIN", "MTLR", "SMLT", "OZON", "TCSG"
]

# Paths
from pathlib import Path
DB_PATH = Path(__file__).parent / "brain.db"
FINDINGS_PATH = Path(__file__).parent / "findings.json"
