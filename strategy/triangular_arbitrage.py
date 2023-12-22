import pandas as pd
import time

from strategy.base import StrategyBase


class StrategyTriangular(StrategyBase):
    def __init__(self, lower_profit_limit=10):
        super().__init__()
        self.lower_profit_limit = lower_profit_limit
        self.market_a = 'BTC'
        self.market_b = 'ETH'
        self.common_base_list = []
        # ------------------------------------------------------
        self.market_c = ''
        self.price_ba = 0
        self.price_cb = 0
        self.price_ca = 0
        self.price_ba_ts = 0
        self.price_cb_ts = 0
        self.price_ca_ts = 0

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
                                    == self.market_a]['base'].tolist()
        base_b_list = base_quote_df[base_quote_df['quote']
                                    == self.market_b]['base'].tolist()
        # 获取相同的基础货币列表
        self.common_base_list = list(set(base_a_list) & set(base_b_list))

    def on_next(self, candle):
        # 三角套利这里的candle如果是一个数组，会有点矛盾，每一次新的交易对都要重新计算，但没计算前又不知道是第三个交易对选哪个
        # 所以我们这里candle就只传入时间，方便回测
        select_symbol(since=candle)  # 每一次都重新选出第三个交易对
        self.make_trad()

    def select_symbol(self, since=None):
        for market_c in self.common_base_list:
            ba = self.market_b + '/' + self.market_a
            cb = market_c + '/' + self.market_b
            ca = market_c + '/' + self.market_a
            p1, p1_ts = self._fetch_ohlcv_safe(ba, since=since)
            p2, p2_ts = self._fetch_ohlcv_safe(cb, since=since)
            p3, p3_ts = self._fetch_ohlcv_safe(ca, since=since)
            if p1 == 0 or p2 == 0 or p3 == 0:
                continue
            cur_ts = self.exchange.milliseconds()
            if not _is_in_one_sec(cur_ts, p1_ts, p2_ts, p3_ts):
                continue
            profit = (p3 / (p1 * p2) - 1) * 1000
            print('market_c={}, profit={}'.format(market_c, profit))
            if profit > self.lower_profit_limit:
                self.market_a = market_a
                self.market_b = market_b
                self.market_c = market_c
                self.price_ba = p1
                self.price_cb = p2
                self.price_ca = p3
                self.price_ba_ts = p1_ts
                self.price_cb_ts = p2_ts
                self.price_ca_ts = p3_ts
                return

    def make_trad(self):
        pass

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
