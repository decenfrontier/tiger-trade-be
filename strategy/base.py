import time

from model.const import OrderStatus
from pkg.xlog import logger


class StrategyBase:
    def __init__(self, exchange):
        self.exchange = exchange

    def on_start(self):
        logger.info("on_start")

    def on_stop(self):
        logger.info("on_stop")

    def waiting_for_order_finished(self, order_id, extra_info=''):
        start_time = time.time()
        while True:
            order = self.exchange.fetch_order(order_id)
            if order['status'] in [OrderStatus.Closed, OrderStatus.Filled]:
                logger.info(f"[waiting_for_order_finished]order finished|order_id={order_id}|{extra_info}")
                # TODO: 这里最好加个监控, 预期价格，实际成交价格, 下单时间, 成交时间
                return True
            time.sleep(self.exchange.rateLimit / 1000)
            if time.time() - start_time > 10:  # 10秒后还没成交, 自动取消
                logger.error(f"[waiting_for_order_finished]order timeout|order_id={order_id}|{extra_info}")
                return False

    def get_balance(self, currency):
        balance = self.exchange.fetch_balance()
        return balance['free'][currency]

    def on_next(self, candle):
        raise NotImplementedError("on_next must be implemented")

    def select_symbol(self):
        raise NotImplementedError("select_stock must be implemented")

    def make_trad(self):
        raise NotImplementedError("make_trad must be implemented")

    def make_trad_backtest(self):
        raise NotImplementedError("make_trad_backtest must be implemented")