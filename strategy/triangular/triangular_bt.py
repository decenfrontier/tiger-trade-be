from model.order import OrderData
from strategy.triangular.triangular import StrategyTriangular
from pkg.xlog import logger

class StrategyTriangularBT(StrategyTriangular):
    def make_trad(self):
        # 模拟下单的操作, 来生成order
        symbol_ba = self.currency_b + '/' + self.currency_a
        symbol_cb = self.currency_c + '/' + self.currency_b
        symbol_ca = self.currency_c + '/' + self.currency_a
        # 先用A换B
        amount_a = self.cur_cash  # 当前的现金数 就是 a的数量
        self.order_ba = OrderData.generate_mock_order(symbol_ba, self.price_ba, amount_a, side='buy', status='closed')
        # 再用B换C, 要先从order的信息中获取成交价是多少, 然后 amount_a 能换出多少amount_b
        # 比如说a的数量为200， 然后b/a的价格为10， 即1个b能换10个a， 所以b的数量是200/10
        amount_b = amount_a / self.price_ba
        self.order_cb = OrderData.generate_mock_order(symbol_cb, self.price_cb, amount_b, side='buy', status='closed')
        # 再用C换A
        amount_c = amount_b / self.price_cb
        self.order_ca = OrderData.generate_mock_order(symbol_ca, self.price_ca, amount_c, side='sell', status='closed')
        ori_cash = self.cur_cash

        amount_a = amount_c * self.price_ca
        self.cur_cash = amount_a
        logger.info('[make_trad_bt] make_trade success, ori_cash={}, cur_cash={}'.format(ori_cash, self.cur_cash))
