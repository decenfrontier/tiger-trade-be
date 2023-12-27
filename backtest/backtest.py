import ccxt

import pandas as pd

from strategy.triangular.triangular_bt import StrategyTriangularBT


class BackTester:
	def __init__(self, exchange, data, strategy_cls, leverage=1.0, commission=0.00075, slippage=0.01, initial_cash=100000):
		self.data = data  # 回测数据,
		self.exchange = exchange
		self.initial_cash = initial_cash  # 初始资金，默认10万
		self.strategy_inst = strategy_cls(self.exchange, self.initial_cash)  # 策略实例
		self.leverage = leverage  # 杠杆率
		self.commission = commission  # 手续费 (0.075%)
		self.slippage = slippage  # 滑点
		# ------------------------------------------------------
		self.trades = []  # 已完成的交易清单
		self.ongoing_orders = []  # 还未成交的订单

	def run(self):
		self.trades = []  # 每次运行回测清空之前的交易记录
		self.strategy_inst.on_start()
		for index, candle in self.data.iterrows():
			candle_value = candle.values[0]
			self.strategy_inst.on_next(candle_value)
		self.strategy_inst.on_stop()

	# 净利润, 利润率, 年化利润率
	def calculate(self):
		net_profit = self.strategy_inst.cur_cash - self.initial_cash
		net_profit_rate = net_profit / self.initial_cash * 100
		# annualized_profit_rate = (1 + net_profit_rate / 100) ** (1 / len(self.trades)) - 1
		print(f"净利润:{net_profit}, 利润率:{net_profit_rate}%")


if __name__ == '__main__':
	data = pd.read_csv('./triangular/bt_data.csv')
	exchange = ccxt.binance({
		'timeout': 15000,
		'enableRateLimit': True,
		'proxies': {
			'https': 'http://127.0.0.1:7897',
			'http': 'http://127.0.0.1:7897'
		}
	})
	bt = BackTester(exchange, data, StrategyTriangularBT)
	bt.run()
	bt.calculate()
