import pandas as pd
from datetime import datetime
import time

from strategy.base import StrategyBase
from pkg.xlog import logger
from utils.utils import calc_func_elapsed_time, save_obj_into_file, load_obj_from_file
from model.order import OrderData


class StrategyTriangular(StrategyBase):
    def __init__(self, exchange, current_cash=0, lower_profit_limit=1, currency_a='USDT', currency_b='BNB'):
        super().__init__(exchange, current_cash)
        self.lower_profit_limit = lower_profit_limit
        self.currency_a = currency_a
        self.currency_b = currency_b
        self.per_soha_rate = 0.8  # 每次交易梭哈比例, 注意不能填1, 因为还要留点钱付手续费
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
        # 先要查一下有没有 B/A 的交易对
        symbols = list(markets.keys())
        symbol_ba = self.currency_b + '/' + self.currency_a
        if symbol_ba not in symbols:
            raise Exception(f'B/A symbol {symbol_ba} not in symbols')
        # 找到同时以A和B计价的交易对
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
        # 但有些虽然在 keys 中, 实际上是获取不到ticker数据的, 也要从交集中移除
        self._remove_invalid_symbol()
        logger.info(f'[triangular] on_start, There are {len(self.common_base_list)} currencies denominated in these two currencies')
        logger.info(f'[triangular] on_start, exchange_rate_limit={self.exchange.rateLimit}')

    def on_next(self, since):
        if since:
            logger.info(f'[triangular] on_next, since={datetime.fromtimestamp(since / 1000)}------------------')
        else:
            logger.info(f'[triangular] on_next, cur_time={datetime.now()}------------------')
        # 每次迭代清空之前的交易记录
        self.clear_temp_data()
        # 三角套利这里的candle如果是一个数组，会有点矛盾，每一次新的交易对都要重新计算，但没计算前又不知道是第三个交易对选哪个
        # 所以我们这里candle就只传入时间，方便回测
        if self.select_symbol(since=since):  # 每一次都重新选出第三个交易对
            self.make_trad()

    def select_symbol(self, since=None):
        max_profit = -9999
        max_profit_currency_c = ''
        max_profit_ts = 0
        for currency_c in self.common_base_list:
            ba = self.currency_b + '/' + self.currency_a
            cb = currency_c + '/' + self.currency_b
            ca = currency_c + '/' + self.currency_a
            p1, p1_ts = self._get_symbol_price_timestamp(ba, since=since)
            if p1 == 0:
                continue
            p2, p2_ts = self._get_symbol_price_timestamp(cb, since=since)
            if p2 == 0:
                continue
            p3, p3_ts = self._get_symbol_price_timestamp(ca, since=since)
            if p3 == 0:
                continue
            if since is None:
                cur_ts = self.exchange.milliseconds()
                if not self._is_in_valid_time(cur_ts, p1_ts, p2_ts, p3_ts):
                    continue
            profit = (p3 / (p1 * p2) - 1) * 1000
            logger.info('currency_c={}, profit={}, ts={}'.format(currency_c, profit, p3_ts))
            if profit > max_profit:
                max_profit = profit
                max_profit_currency_c = currency_c
                max_profit_ts = p3_ts
            if profit > self.lower_profit_limit:  # 利润超过设定的下限，可以进行三角套利
                self.currency_c = currency_c
                self.price_ba = p1
                self.price_cb = p2
                self.price_ca = p3
                self.price_ba_ts = p1_ts
                self.price_cb_ts = p2_ts
                self.price_ca_ts = p3_ts
                logger.info('[triangular] select_symbol success|currency_c={}, profit={}, ts={}'.format(
                    currency_c, max_profit, p3_ts))
                return True
        logger.info('[triangular] select_symbol failed|currency_c={}, max_profit={}, ts={}'.format(
                max_profit_currency_c, max_profit, max_profit_ts))
        return False

    def make_trad(self):
        if self.currency_c == '':
            return
        symbol_ba = self.currency_b + '/' + self.currency_a
        symbol_cb = self.currency_c + '/' + self.currency_b
        symbol_ca = self.currency_c + '/' + self.currency_a
        # 先用A换B
        amount_a = self.get_balance(self.currency_a)
        logger.info(f'[triangular] make_trad a->b|symbol_ba={symbol_ba}, amount_a={amount_a}')
        self.order_ba = self.exchange.create_market_order_with_cost(symbol_ba, 'buy', amount_a)  # 此函数交易以 quote 为单位
        if not self.waiting_for_order_finished(self.order_ba['id'], symbol_ba, extra_info='a -> b'):
            raise Exception(f"[triangular] make_trad a->b|symbol_ba={symbol_ba}, amount_a={amount_a}, order_id={self.order_ba['id']}")
        # 再用B换C, 这里可能是冷门交易对, 有价无市, 我们要买, 但没有人卖, 导致交易过期
        amount_b = self.get_balance(self.currency_b)
        logger.info(f'[triangular] make_trad b->c|symbol_cb={symbol_cb}, amount_b={amount_b}')
        self.order_cb = self.exchange.create_market_order_with_cost(symbol_cb, 'buy', amount_b)  # 此函数交易以 quote 为单位
        if not self.waiting_for_order_finished(self.order_cb['id'], symbol_cb, extra_info='b -> c'):
            return
        # 再用C换A, 比如C是QKC, 找不到BTC/QKC, 只能找QKC/BTC, 然后卖出QKC, 得到BTC
        amount_c = self.get_balance(self.currency_c)
        logger.info(f'[triangular] make_trad c->a|symbol_ca={symbol_ca}, amount_c={amount_c}')
        self.order_ca = self.exchange.create_order(symbol_ca, 'market', 'sell', amount_c)  # 此函数交易以 base 为单位
        self.waiting_for_order_finished(self.order_ca['id'], symbol_ca, extra_info='c -> a')

    # @calc_func_elapsed_time
    def _get_symbol_price_timestamp(self, symbol, since=None):
        try:
            if since:
                tohlcv = self.exchange.fetch_ohlcv(symbol, timeframe='1s', limit=1, since=since)[0]
                return tohlcv[4] or 0, tohlcv[0] or 0
            else:
                ticker = self.exchange.fetch_ticker(symbol)
                return ticker['last'] or 0, ticker['timestamp'] or 0
        except Exception as e:
            logger.warning(f"_fetch_ohlcv_safe, error: {e}")
            return 0, 0

    def _is_in_valid_time(self, cur_ts, p1_ts, p2_ts, p3_ts):
        return abs(cur_ts - p1_ts) < 1500 and abs(cur_ts - p2_ts) < 1500 and abs(cur_ts - p3_ts) < 1500

    def _remove_invalid_symbol(self):
        # 优先读配置文件
        config_file = f"../config/binance-{self.currency_a}-{self.currency_b}.bin"
        config_common_list = load_obj_from_file(config_file)
        if isinstance(config_common_list, list):
            self.common_base_list = config_common_list
            return
        # 没读到再筛选
        for i, currency_c in enumerate(self.common_base_list):
            symbol_cb = currency_c + "/" + self.currency_b
            symbol_ca = currency_c + "/" + self.currency_a
            p2, _ = self._get_symbol_price_timestamp(symbol_cb)
            p3, _ = self._get_symbol_price_timestamp(symbol_ca)
            if p2 == 0 or p3 == 0:
                self.common_base_list.pop(i)
                i -= 1  # 每次 pop 之后, for 会i+1, 但此时i已经指向了下一个元素, 所以需要i-1
        # 筛选结束后保存为配置文件, 下次直接读配置
        save_obj_into_file(self.common_base_list, config_file)



if __name__ == '__main__':
    StrategyTriangular().select_symbol()
