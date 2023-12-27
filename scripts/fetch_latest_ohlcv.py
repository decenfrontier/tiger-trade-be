import ccxt
from datetime import datetime
from utils.utils import calc_func_elapsed_time


exchange = ccxt.binance({'timeout': 15000,
                         'enableRateLimit': False,
                         'proxies': {
                             'https': 'http://127.0.0.1:7890',
                             'http': 'http://127.0.0.1:7890'
                         }})


@calc_func_elapsed_time
def method1():
    data = exchange.fetch_ohlcv('BTC/USDT', '1s', limit=1)
    print(datetime.fromtimestamp(data[0][0] / 1000).strftime('%Y-%m-%d %H:%M:%S'))
    # 如果要加上 since 的话, 要比当前时间提前至少2秒, 不然会报错
    # since = exchange.milliseconds() - 2000
    # print(since)
    # data = exchange.fetch_ohlcv('BTC/USDT', '1s', since=since, limit=1)
    # print(datetime.fromtimestamp(data[0][0] / 1000).strftime('%Y-%m-%d %H:%M:%S'))
    # print(data)
    # print(exchange.rateLimit)


@calc_func_elapsed_time
def method2():
    data = exchange.fetch_ticker('BTC/USDT')
    print(datetime.fromtimestamp(data['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S'))


if __name__ == '__main__':
    exchange.load_markets()
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    method1()
    method2()
