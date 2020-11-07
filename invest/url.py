"""
url.py
~~~~~~

Contains URLs/APIs for statements
"""

import logging
import requests
from enum import Enum
from constants import StockCode, InvestIndicators

logger = logging.getLogger("URL")


class Statements:
    _name = ""

    _main_indicators = "@CODE@"
    _balance_statements = "@CODE@"
    _income_statements = "@CODE@"
    _cash_flow_statements = "@CODE@"

    _headers = {'User-Agent': 'Mozilla/5.0'}

    def __init__(self, code):
        self._code = code
        self._main_indicators = self._main_indicators.replace("@CODE@", code)
        self._balance_statements = self._balance_statements.replace("@CODE@", code)
        self._income_statements = self._income_statements.replace("@CODE@", code)
        self._cash_flow_statements = self._cash_flow_statements.replace("@CODE@", code)

    @property
    def code(self):
        return self._code

    @property
    def name(self):
        return self._name

    @property
    def main_indicators(self):
        return self._main_indicators

    @property
    def balance_statements(self):
        return self._balance_statements

    @property
    def income_statements(self):
        return self._income_statements

    @property
    def cash_flow_statements(self):
        return self._cash_flow_statements


class HithinkFlushStatements(Statements):
    _name = "HithinkFlush"

    _main_indicators = \
        "http://basic.10jqka.com.cn/api/usa/export.php?export=keyindex&type=report&code=@CODE@"
    _balance_statements = \
        "http://basic.10jqka.com.cn/api/usa/export.php?export=debt&type=report&code=@CODE@"
    _income_statements = \
        "http://basic.10jqka.com.cn/api/usa/export.php?export=benefit&type=report&code=@CODE@"
    _cash_flow_statements = \
        "http://basic.10jqka.com.cn/api/usa/export.php?export=cash&type=report&code=@CODE@"

    def get_main_indicators(self):
        pass

    def get_balance_statements(self):
        pass

    def get_income_statements(self):
        pass

    def get_cash_flow_statements(self):
        pass


class SnowballStatements(Statements):
    _name = "Snowball"

    _main_indicators = \
        "https://stock.xueqiu.com/v5/stock/finance/us/indicator.json?symbol=@CODE@&type=Q4&is_detail=true&count=100"
    _balance_statements = \
        "https://stock.xueqiu.com/v5/stock/finance/us/balance.json?symbol=@CODE@&type=Q4&is_detail=true&count=100"
    _income_statements = \
        "https://stock.xueqiu.com/v5/stock/finance/us/income.json?symbol=@CODE@&type=Q4&is_detail=true&count=100"
    _cash_flow_statements = \
        "https://stock.xueqiu.com/v5/stock/finance/us/cash_flow.json?symbol=@CODE@&type=Q4&is_detail=true&count=100"

    def __init__(self, code):
        super().__init__(code)
        self._session = requests.Session()
        self._session.get("https://xueqiu.com/", headers=self._headers)

    def get_main_indicators(self):
        resp = self._session.get(self._main_indicators, headers=self._headers)
        if resp.status_code != 200:
            logger.warning(f"{self._name} - Failed to get main indicators ({resp.status_code})")
            return None
        return resp.json()

    def get_balance_statements(self):
        resp = self._session.get(self._balance_statements, headers=self._headers)
        if resp.status_code != 200:
            logger.warning(f"{self._name} - Failed to get balance statements ({resp.status_code})")
            return None
        return resp.json()

    def get_income_statements(self):
        resp = self._session.get(self._income_statements, headers=self._headers)
        if resp.status_code != 200:
            logger.warning(f"{self._name} - Failed to get income statements ({resp.status_code})")
            return None
        return resp.json()

    def get_cash_flow_statements(self):
        resp = self._session.get(self._cash_flow_statements, headers=self._headers)
        if resp.status_code != 200:
            logger.warning(f"{self._name} - Failed to get cash flow statements ({resp.status_code})")
            return None
        return resp.json()

    def get_invest_indicators(self):
        invest_indicators = {}
        balance_statements = self.get_balance_statements().get("data").get("list")
        for balance_statement in balance_statements:
            report_annual = balance_statement.get("report_annual")
            invest_indicators.update({report_annual: {}}) if report_annual not in invest_indicators else None
            required_info = invest_indicators.get(report_annual)
            required_info.update({InvestIndicators.DCF.value: balance_statement.get("total_cash")[0]})
            capital_stock = balance_statement.get("common_stock")[0]
            capital_stock += balance_statement.get("preferred_stock")[0] \
                if balance_statement.get("preferred_stock")[0] is not None else 0
            capital_stock += balance_statement.get("add_paid_in_capital")[0] \
                if balance_statement.get("add_paid_in_capital")[0] is not None else 0
            required_info.update({InvestIndicators.CAPITAL_STOCK.value: capital_stock})

        income_statements = self.get_income_statements().get("data").get("list")
        for income_statement in income_statements:
            report_annual = income_statement.get("report_annual")
            invest_indicators.update({report_annual: {}}) if report_annual not in invest_indicators else None
            required_info = invest_indicators.get(report_annual)
            required_info.update({InvestIndicators.EPS.value: income_statement.get("total_basic_earning_common_ps")[0]})
            required_info.update({InvestIndicators.SALES.value: income_statement.get("total_revenue")[0]})

            if InvestIndicators.CAPITAL_STOCK.value in invest_indicators.get(report_annual):
                capital_stock = invest_indicators.get(report_annual).get(InvestIndicators.CAPITAL_STOCK.value)
                roic = income_statement.get("income_from_co")[0] / capital_stock
                required_info.update({InvestIndicators.ROIC.value: roic})

        # pprint(income_statements)
        # pprint(balance_statements)
        return invest_indicators


class Platforms(Enum):
    Snowball = SnowballStatements
    HithinkFlush = HithinkFlushStatements


def get_invest_indicators(code, platform=Platforms.Snowball):
    return platform.value(code.value).get_invest_indicators()


def get_main_indicators(code, platform=Platforms.Snowball):
    return platform.value(code.value).get_main_indicators()


def get_balance_statements(code, platform=Platforms.Snowball):
    return platform.value(code.value).get_balance_statements()


def get_income_statements(code, platform=Platforms.Snowball):
    return platform.value(code.value).get_income_statements()


def get_cash_flow_statements(code, platform=Platforms.Snowball):
    return platform.value(code.value).get_cash_flow_statements()


def get_all_statements(code, platform=Platforms.Snowball):
    return dict(main_indicators=get_main_indicators(code, platform=platform),
                balance_statement=get_balance_statements(code, platform=platform),
                income_statement=get_income_statements(code, platform=platform),
                cash_flow_statement=get_cash_flow_statements(code, platform=platform))


if __name__ == "__main__":
    from pprint import pprint

    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(name)-8s %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S',
                        level=logging.INFO)

    pprint(get_invest_indicators(StockCode.NETFLIX, Platforms.Snowball))
    # pprint(get_main_indicators(StockCode.NETFLIX, Platforms.Snowball))
    # pprint(get_balance_statements(StockCode.NETFLIX, Platforms.Snowball))
    # pprint(get_income_statements(StockCode.NETFLIX, Platforms.Snowball))
    # pprint(get_cash_flow_statements(StockCode.NETFLIX, Platforms.Snowball))
