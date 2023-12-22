from datetime import datetime
import sys
import ccxt
import pandas as pd

exchange = ccxt.binance({'timeout': 15000,
                         'enableRateLimit': True,
                         'proxies': {
                             'https': 'http://127.0.0.1:7897',
                             'http': 'http://127.0.0.1:7897'
                         }})


def download(symbol, from_ts, end_ts, timeframe):
    data = []
    tf = exchange.parse_timeframe(timeframe)
    time_delta_sec = (int(end_ts) - int(from_ts)) / 1000
    ticker_count = 1 + time_delta_sec / tf
    while True:
        origin_len = len(data)
        new_data = exchange.fetch_ohlcv(symbol, timeframe, int(from_ts), limit=1000)
        data.extend(new_data)
        if len(data) >= ticker_count or from_ts >= end_ts or origin_len == len(data):
            break
        from_ts = int(data[-1][0]) + 1
        print('process={}, from_ts={}'.format(len(data) / ticker_count, from_ts))
    return data


def save_as_csv(data, file_name='back_trade.csv'):
    header = ['t', 'o', 'h', 'l', 'c', 'v']
    df = pd.DataFrame(data, columns=header)
    # df.set_index('t', inplace=True)
    df.to_csv(file_name, index=False)


if __name__ == '__main__':
    # 用法： python fetch_back_trade.py BTC/USDT 2022-01-01 2h
    symbol = sys.argv[1]
    start_date = sys.argv[2]
    timeframe = sys.argv[3]

    end_date = str(datetime.now())[:19]
    from_ts = exchange.parse8601(f'{start_date} 00:00:00')
    end_ts = exchange.parse8601(f'{end_date} 00:00:00')

    data = download(symbol, from_ts, end_ts, timeframe)
    save_as_csv(data)
