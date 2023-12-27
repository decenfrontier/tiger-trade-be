import ccxt
import os

print(os.getenv('BA_TEST_API_KEY'))

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

# 获取账户余额
balances = exchange.fetch_balance()

# 输出账户余额信息
for currency, balance in balances['total'].items():
    print(f"Currency: {currency}, Balance: {balance}")

# order = exchange.create_order(symbol='ETH/USDT', type='market', side='buy', amount=1)
# print(order)
