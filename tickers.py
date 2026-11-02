TIER1 = ["SBER", "GAZP", "LKOH", "GMKN", "ROSN", "NVTK", "TATN", "PLZL"]
TIER2 = ["MTSS", "MGNT", "CHMF", "NLMK", "ALRS", "MOEX", "SNGS", "VTBR", "PHOR", "RUAL", "AFLT", "IRAO", "HYDR", "PIKK", "FEES"]
TIER3 = ["SFIN", "MTLR", "SMLT", "OZON", "TCSG", "POLY"]

TICKERS = sorted(set(TIER1 + TIER2 + TIER3))


def tier_of(ticker: str) -> int:
    if ticker in TIER1:
        return 1
    if ticker in TIER2:
        return 2
    return 3
