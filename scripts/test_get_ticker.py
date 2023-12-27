import ccxt

exchange = ccxt.binance({'timeout': 15000,
                         'enableRateLimit': False,
                         'proxies': {
                             'https': 'http://127.0.0.1:7890',
                             'http': 'http://127.0.0.1:7890'
                         }})


ticker = exchange.fetch_ticker('BAT/BNB')
print(ticker)