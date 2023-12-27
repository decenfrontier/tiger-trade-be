import time

import ccxt

from model.trade import TradeData
import matplotlib.pyplot as plt


class BackTester:
	def __init__(self, data, strategy_cls, leverage, commission, slippage, initial_cash=100000):
		self.exchange = ccxt.binance({
			'timeout': 15000,
			'enableRateLimit': True,
			'proxies': {
				'https': 'http://127.0.0.1:7897',
				'http': 'http://127.0.0.1:7897'
			}
		})
		self.data = data  # 回测数据
		self.strategy_cls = strategy_cls  # 策略
		self.leverage = leverage  # 杠杆率
		self.commission = commission  # 手续费
		self.slippage = slippage  # 滑点
		self.initial_cash = initial_cash  # 初始资金，默认10万
		# ------------------------------------------------------
		self.trades = []  # 已完成的交易清单
		self.ongoing_orders = []  # 还未成交的订单

	def run(self):
		self.trades = []  # 每次运行回测清空之前的交易记录
		strategy_inst = self.strategy_cls(self.exchange)
		strategy_inst.on_start()
		for index, candle in self.data.iterrows():
			strategy_inst.on_next(candle)
		strategy_inst.on_stop()
		self.calculate()

	# 净利润，利润率
	def calculate(self):
		x = []  # 横轴=交易时间
		y = []  # 纵轴=净利润
		while len(self.trades) >= 3:
			# 每三个交易为一组，逐组计算利润
			trade3 = self.trades[:3]
			profit3 = 0
			for trade in trade3:
				if trade.side == 'buy':
					profit3 -= trade.price * trade.amount
				else:
					ts = trade.ts
					x.append(ts)
					profit3 += trade.price * trade.amount
			y.append(profit3)
			self.trades = self.trades[3:]
		plt.plot(x, y)
		plt.show()




if __name__ == '__main__':
	a = [0, 1, 2]
	print(a[3:])