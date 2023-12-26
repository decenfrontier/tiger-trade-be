import pandas as pd
import time

from strategy.base import StrategyBase
from pkg.xlog import logger
from model.order import OrderData


class StrategyTriangular(StrategyBase):
    def __init__(self, exchange, initial_cash, lower_profit_limit=10, currency_a='BTC', currency_b='ETH'):
        super().__init__(exchange, initial_cash)
        self.lower_profit_limit = lower_profit_limit
        self.currency_a = currency_a
        self.currency_b = currency_b
        self.common_base_list = []
        self.clear_temp_data()

    def clear_temp_data(self):
        self.currency_c = ''
        self.price_ba = 0
        self.price_cb = 0
        self.price_ca = 0
        self.price_ba_ts = 0
        self.price_cb_ts = 0
        self.price_ca_ts = 0
        self.order_ba = None
        self.order_cb = None
        self.order_ca = None

    def on_start(self):
        # 加载行情
        markets = self.exchange.load_markets()
        # 找到同时以A和B计价的交易对
        symbols = list(markets.keys())
        symbols_df = pd.DataFrame(symbols, columns=['symbol'])
        # 分割字符串得到 基础货币/计价货币
        base_quote_df = symbols_df['symbol'].str.split('/', expand=True)
        base_quote_df.columns = ['base', 'quote']
        # 过滤得到以 A B 计价的计价货币
        base_a_list = base_quote_df[base_quote_df['quote']
                                    == self.currency_a]['base'].tolist()
        base_b_list = base_quote_df[base_quote_df['quote']
                                    == self.currency_b]['base'].tolist()
        # 获取相同的基础货币列表
        self.common_base_list = list(set(base_a_list) & set(base_b_list))

    def on_next(self, candle, is_backtest=False):
        # 每次迭代清空之前的交易记录
        self.clear_temp_data()
        # 三角套利这里的candle如果是一个数组，会有点矛盾，每一次新的交易对都要重新计算，但没计算前又不知道是第三个交易对选哪个
        # 所以我们这里candle就只传入时间，方便回测
        self.select_symbol(since=candle)  # 每一次都重新选出第三个交易对
        ongoing_orders = self.make_trad(is_backtest)
        return ongoing_orders

    def select_symbol(self, since=None):
        for currency_c in self.common_base_list:
            ba = self.currency_b + '/' + self.currency_a
            cb = currency_c + '/' + self.currency_b
            ca = currency_c + '/' + self.currency_a
            p1, p1_ts = self._fetch_ohlcv_safe(ba, since=since)
            p2, p2_ts = self._fetch_ohlcv_safe(cb, since=since)
            p3, p3_ts = self._fetch_ohlcv_safe(ca, since=since)
            if p1 == 0 or p2 == 0 or p3 == 0:
                continue
            cur_ts = self.exchange.milliseconds()
            if not _is_in_one_sec(cur_ts, p1_ts, p2_ts, p3_ts):
                continue
            profit = (p3 / (p1 * p2) - 1) * 1000
            logger.info('currency_c={}, profit={}'.format(currency_c, profit))
            if profit > self.lower_profit_limit:
                self.currency_c = currency_c
                self.price_ba = p1
                self.price_cb = p2
                self.price_ca = p3
                self.price_ba_ts = p1_ts
                self.price_cb_ts = p2_ts
                self.price_ca_ts = p3_ts
                return

    def make_trad(self, is_backtest=False):
        if self.currency_c == '':
            return
        if is_backtest:
            return self.make_trad_backtest()
        symbol_ba = self.currency_b + '/' + self.currency_a
        symbol_cb = self.currency_c + '/' + self.currency_b
        symbol_ca = self.currency_c + '/' + self.currency_a
        # 先用A换B
        amount_a = self.get_balance(self.currency_a)
        self.order_ba = self.exchange.create_order(symbol_ba, 'market', 'buy', amount=amount_a)
        if not self.waiting_for_order_finished(self.order_ba['id'], extra_info='a -> b'):
            return
        # 再用B换C
        amount_b = self.get_balance(self.currency_b)
        self.order_cb = self.exchange.create_order(symbol_cb, 'market', 'buy', amount=amount_b)
        if not self.waiting_for_order_finished(self.order_cb['id'], extra_info='b -> c'):
            return
        # 再用C换A, 比如C是QKC, 找不到BTC/QKC, 只能找QKC/BTC, 然后卖出QKC, 得到BTC
        amount_c = self.get_balance(self.currency_c)
        self.order_ca = self.exchange.create_order(symbol_ac, 'market', 'sell', amount=amount_ca)
        self.waiting_for_order_finished(self.order_ca['id'], extra_info='c -> a')


    def make_trad_backtest(self):
        symbol_ba = self.currency_b + '/' + self.currency_a
        symbol_cb = self.currency_c + '/' + self.currency_b
        symbol_ca = self.currency_c + '/' + self.currency_a
        amount_ba = self.current_cash // self.price_ba
        amount_cb = self.current_cash // self.price_cb
        amount_ca = self.current_cash // self.price_ca
        # 模拟下单的操作, 来生成order
        self.order_ba = OrderData.generate_mock_order(symbol_ba, self.price_ba, amount_ba)
        self.order_cb = OrderData.generate_mock_order(symbol_cb, self.price_cb, amount_cb)
        self.order_ca = OrderData.generate_mock_order(symbol_ca, self.price_ca, amount_ca, side='sell')
        return [self.order_ba, self.order_cb, self.order_ca]


    def _fetch_ohlcv_safe(self, symbol, since=None):
        try:
            tohlcv = self.exchange.fetch_ohlcv(symbol, timeframe='1s', limit=1, since=since)[0]
            return tohlcv[4] or 0, tohlcv[0] or 0
        except Exception as e:
            return 0, 0

    def _is_in_one_sec(self, cur_ts, p1_ts, p2_ts, p3_ts):
        return abs(cur_ts - p1_ts) < 1000 and abs(cur_ts - p2_ts) < 1000 and abs(cur_ts - p3_ts) < 1000


if __name__ == '__main__':
    StrategyTriangular().select_symbol()
