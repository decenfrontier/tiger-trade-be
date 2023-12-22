class BackTester:
	def __init__(self, data, strategy_cls, leverage, commission, initial_cash=100000):
		self.data = data  # 回测数据
		self.strategy_cls = strategy_cls  # 策略
		self.leverage = leverage  # 杠杆率
		self.commission = commission  # 手续费
		self.initial_cash = initial_cash  # 初始资金，默认10万
		# ------------------------------------------------------
		self.trades = []  # 已完成的交易
		self.ongoing_orders = []  # 还未成交的订单

	def run(self):
		self.trades = []  # 每次运行回测清空之前的交易记录
		strategy_inst = self.strategy_cls()
		strategy_inst.on_start()
		for index, candle in self.data.iterrows():
			strategy_inst.on_next(candle)
			pass
		strategy_inst.on_stop()
		profit = self.calculate()
		print('profit={}', profit)

	# 夏普率, 盈亏比, 胜率, 最大回撤, 年化利率
	def calculate(self):
		for trade in self.trades:
			pass
		return 1,2,3,4
