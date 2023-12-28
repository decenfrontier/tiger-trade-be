import time

import ccxt
import os

from model.const import OrderStatus
from pkg.xlog import logger


exchange = ccxt.binance({
    'apiKey': os.getenv('BA_TEST_API_KEY'),
    'secret': os.getenv('BA_TEST_SECRET'),
    'timeout': 15000,
    'enableRateLimit': True,
    'proxies': {
        'https': 'http://127.0.0.1:7890',
        'http': 'http://127.0.0.1:7890'
    }
})
exchange.set_sandbox_mode(True)


def waiting_for_order_finished(order_id, symbol, extra_info=''):
    start_time = time.time()
    while True:
        order = exchange.fetch_order(order_id, symbol=symbol)
        if order['status'] in [OrderStatus.Closed, OrderStatus.Filled]:
            logger.info(f"[waiting_for_order_finished]order finished|order_id={order_id}|{extra_info}")
            # TODO: 这里最好加个监控, 预期价格，实际成交价格, 下单时间, 成交时间
            return True
        if time.time() - start_time > 10:  # 10秒后还没成交
            logger.error(f"[waiting_for_order_finished]order timeout|order_id={order_id}|{extra_info}")
            return False


def sell_symbol():
    currency_a = 'USDT'
    currency_c = 'ETH'
    symbol_ca = f'{currency_c}/{currency_a}'
    # 获取账户余额
    balances = exchange.fetch_balance()
    amount_a = balances['free'][currency_a]
    amount_c = balances['free'][currency_c]
    logger.info(f'交易前, amount_c:{amount_c}, amount_a:{amount_a}')
    order = exchange.create_order(symbol_ca, 'market', 'sell', amount_c)  # amount 以 base 为单位
    waiting_for_order_finished(order['id'], symbol_ca)

    balances = exchange.fetch_balance()
    amount_a = balances['free'][currency_a]
    amount_c = balances['free'][currency_c]
    logger.info(f'交易后, amount_c:{amount_c}, amount_a:{amount_a}')


def print_balance():
    # 获取账户余额
    balances = exchange.fetch_balance()
    # 输出账户余额信息
    for currency, balance in balances['total'].items():
        print(f"Currency: {currency}, Balance: {balance}")


def buy_symbol():
    order = exchange.create_order(symbol='ETH/USDT', type='market', side='buy', amount=1)
    print(order)


def get_order_status(order_id, symbol):
    order = exchange.fetch_order(order_id, symbol)
    print(order['status'])


def get_order_book(symbol):  # 比如symbol 是 RAY/BNB
    order_book = exchange.fetch_order_book(symbol)
    # 输出卖单信息（卖出 RAY）
    asks = order_book['asks']
    for ask in asks:
        price, amount = ask
        print(f"Sell: Price {price} BNB, Amount {amount} RAY")
    # 输出买单信息（购买 RAY）
    bids = order_book['bids']
    for bid in bids:
        price, amount = bid
        print(f"Buy: Price {price} BNB, Amount {amount} RAY")


get_order_book('RAY/BNB')
