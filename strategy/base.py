from pkg.xlog import logger


class StrategyBase:
    def __init__(self, exchange, initial_cash):
        self.exchange = exchange
        self.initial_cash = initial_cash

    def on_start(self):
        logger.info("on_start")

    def on_stop(self):
        logger.info("on_stop")

    def on_next(self, candle) -> []:
        raise NotImplementedError("on_next must be implemented")

    def select_symbol(self):
        raise NotImplementedError("select_stock must be implemented")

    def make_trad(self):
        raise NotImplementedError("make_trad must be implemented")
