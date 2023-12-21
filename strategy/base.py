import ccxt


class BaseStrategy:
	def __init__(self):
		self.exchange = ccxt.binance({
			'timeout': 15000,
			'enableRateLimit': True,
			'proxies': {
				'https': 'http://127.0.0.1:7897',
				'http': 'http://127.0.0.1:7897'
			}
		})

	def calc(self):
		pass
