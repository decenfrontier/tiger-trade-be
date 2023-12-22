import ccxt
from datetime import datetime

exchange = ccxt.binance({'timeout': 15000,
                         'enableRateLimit': True,
                         'proxies': {
                             'https': 'http://127.0.0.1:7897',
                             'http': 'http://127.0.0.1:7897'
                         }})

exchange.load_markets()
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# 方法1
# data = exchange.fetch_ohlcv('BTC/USDT', '1s', limit=1)
# print(datetime.fromtimestamp(data[0][0] / 1000).strftime('%Y-%m-%d %H:%M:%S'))

# 方法2
# data = exchange.fetch_ticker('BTC/USDT')
# print(datetime.fromtimestamp(data['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S'))

# 方法3, 必须取前2秒, 不然会异常
since = exchange.milliseconds() - 2000
print(since)
data = exchange.fetch_ohlcv('BTC/USDT', '1s', since=since, limit=1)
print(datetime.fromtimestamp(data[0][0] / 1000).strftime('%Y-%m-%d %H:%M:%S'))
print(data)
print(exchange.rateLimit)
