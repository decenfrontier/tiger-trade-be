import os
import time

import ccxt

import pandas as pd

from strategy.triangular.triangular import StrategyTriangular

ENV = 'test'


class Reality:
    def __init__(self, exchange, strategy_cls):
        self.exchange = exchange
        self.strategy_inst = strategy_cls(self.exchange)  # 策略实例
        # ------------------------------------------------------
        self.trades = []  # 已完成的交易清单
        self.ongoing_orders = []  # 还未成交的订单

    def run(self):
        self.strategy_inst.on_start()
        while True:
            self.strategy_inst.on_next(None)
            time.sleep(1)
        self.strategy_inst.on_stop()

    # 净利润, 利润率, 年化利润率
    def calculate(self):
        net_profit = self.strategy_inst.cur_cash - self.initial_cash
        net_profit_rate = net_profit / self.initial_cash * 100
        # annualized_profit_rate = (1 + net_profit_rate / 100) ** (1 / len(self.trades)) - 1
        print(f"net_profit:{net_profit}, net_profit_rate:{net_profit_rate}%")


if __name__ == '__main__':
    exchange = ccxt.binance({
        'apiKey': os.getenv('BA_TEST_API_KEY') if ENV == 'test' else 'BA_API_KEY',
        'secret': os.getenv('BA_TEST_SECRET_KEY') if ENV == 'test' else 'BA_SECRET_KEY',
        'timeout': 15000,
        'enableRateLimit': True,
        'proxies': {
            'https': 'http://127.0.0.1:7897',
            'http': 'http://127.0.0.1:7897'
        }
    })
    bt = Reality(exchange, StrategyTriangular)
    bt.run()
    bt.calculate()
