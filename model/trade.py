class TradeData:
    def __init__(self, ts, symbol, side, trade_type, price, amount):
        self.ts = ts
        self.symbol = symbol
        self.side = side  # buy or sell
        self.trade_type = trade_type  # limit or market
        self.price = price
        self.amount = amount
