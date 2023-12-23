import os
import time

import ccxt

from model.trade import TradeData


class BackTester:
	def __init__(self, data, strategy_cls, leverage, commission, initial_cash=100000):
		self.data = data  # 回测数据
		self.strategy_cls = strategy_cls  # 策略
		self.leverage = leverage  # 杠杆率
		self.commission = commission  # 手续费
		self.initial_cash = initial_cash  # 初始资金，默认10万
		# ------------------------------------------------------
		self.exchange = ccxt.binance({
			'apiKey': os.getenv('TEST_API_KEY'),
			'secret': os.getenv('TEST_SECRET_KEY'),
			'testnet': True,  # 指定为测试环境
			'url': 'https://testnet.binance.vision',  # 指定测试环境的URL
			'timeout': 15000,
			'enableRateLimit': True,
			'proxies': {
				'https': 'http://127.0.0.1:7897',
				'http': 'http://127.0.0.1:7897'
			}
		})
		self.trades = []  # 已完成的交易
		self.ongoing_orders = []  # 还未成交的订单

	def run(self):
		self.trades = []  # 每次运行回测清空之前的交易记录
		strategy_inst = self.strategy_cls(self.exchange)
		strategy_inst.on_start()
		for index, candle in self.data.iterrows():
			ongoing_orders = strategy_inst.on_next(candle)
			self.ongoing_orders.extend(ongoing_orders)
			self.waiting_order_finish()
		strategy_inst.on_stop()
		profit = self.calculate()
		print('profit={}', profit)

	# 夏普率, 盈亏比, 胜率, 最大回撤, 年化利率
	def calculate(self):
		for trade in self.trades:
			pass
		return 1,2,3,4

	# 确定order交易成功再继续
	def waiting_order_finish(self):
		while self.ongoing_orders:
			i = 0
			while self.ongoing_orders:
				if i >= len(self.ongoing_orders):
					break
				order = self.ongoing_orders[i]
				if self.exchange.fetch_order(order['id'])['status'] == 'closed':
					self.ongoing_orders.remove(order)
					self.trades.append(TradeData(order['timestamp'], order['symbol'], order['type'], order['price'], order['amount']))
				else:
					i += 1
				time.sleep(self.exchange.rateLimit / 1000)


if __name__ == '__main__':
	a = [1,2,3]
	b = [4,5,6]

	print(a + b)