"""
constants.py
~~~~~~~~~~~~

Contains constants for invest
"""

from enum import Enum


class StockCode(Enum):
    NETFLIX = "NFLX"
    APPLE = "APPL"
    BILIBILI = "BILI"
    SONY = "SNE"
    DISNEY = "DIS"


class InvestIndicators(Enum):
    ROIC = "return_on_invested_capital"
    CAPITAL_STOCK = "capital_stock"
    EPS = "earnings_per_share"
    SALES = "sales"
    DCF = "discounted_cash_flow"
