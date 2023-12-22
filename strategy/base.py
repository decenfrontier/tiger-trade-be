import ccxt


class StrategyBase:
    def __init__(self):
        self.exchange = ccxt.binance({
            'timeout': 15000,
            'enableRateLimit': True,
            'proxies': {
                'https': 'http://127.0.0.1:7897',
                'http': 'http://127.0.0.1:7897'
            }
        })

    def on_start(self):
        print("on_start")

    def on_stop(self):
        print("on_stop")

    def on_next(self):
        raise NotImplementedError("on_next must be implemented")

    def select_symbol(self):
        raise NotImplementedError("select_stock must be implemented")

    def make_trad(self):
        raise NotImplementedError("make_trad must be implemented")
