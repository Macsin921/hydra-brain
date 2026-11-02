"""Маппинг акций MOEX на ликвидные фьючерсы для FUTOI.
Коды фьючерсов могут меняться по экспирации; здесь указаны базовые коды.
"""

STOCK_TO_FUTURE = {
    "SBER": "SRZ6",
    "GAZP": "GZZ6",
    "LKOH": "LKZ6",
    "GMKN": "GMZ6",
    "ROSN": "RNZ6",
    "NVTK": "NVZ6",
    "TATN": "TTZ6",
    "PLZL": "PGZ6",
    "MTSS": "MTZ6",
    "MGNT": "MNZ6",
    "CHMF": "CHZ6",
    "NLMK": "NMZ6",
    "ALRS": "ALZ6",
    "MOEX": "MMZ6",
    "SNGS": "SNZ6",
    "VTBR": "VBZ6",
    "PHOR": "PHZ6",
    "RUAL": "RUZ6",
    "AFLT": "AFZ6",
    "IRAO": "IRZ6",
    "HYDR": "HYZ6",
    "PIKK": "PKZ6",
    "FEES": "FEZ6",
    "SFIN": "SFZ6",
    "MTLR": "MTZ6",
    "OZON": "OZZ6",
    "TCSG": "TCZ6",
}


def future_for(ticker: str) -> str | None:
    return STOCK_TO_FUTURE.get(ticker)
