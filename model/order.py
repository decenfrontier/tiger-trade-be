import time

from utils.utils import generate_random_number


class OrderData:
    def __init__(self, order_id, timestamp, symbol, order_type, side, price, status, amount):
        self.id = order_id
        self.timestamp = timestamp
        self.symbol = symbol
        self.price = price
        self.amount = amount
        self.order_type = order_type  # limit or market
        self.side = side  # buy or sell
        self.status = status

    @staticmethod
    def generate_mock_order(symbol, price, amount, order_type='market', side='buy', status='open'):
        return OrderData(
            order_id=generate_random_number(7),
            timestamp=int(time.time() * 1000),
            symbol=symbol,
            price=price,
            amount=amount,
            order_type=order_type,
            side=side,
            status=status
        )


# {
#   "info": {
#     "symbol": "ETHUSDT",
#     "orderId": "6453418",
#     "orderListId": "-1",
#     "clientOrderId": "x-R4BD3S824d5ed74de75f64119f9128",
#     "transactTime": "1703342273870",
#     "price": "0.00000000",
#     "origQty": "1.00000000",
#     "executedQty": "1.00000000",
#     "cummulativeQuoteQty": "2292.13000000",
#     "status": "FILLED",
#     "timeInForce": "GTC",
#     "type": "MARKET",
#     "side": "BUY",
#     "workingTime": "1703342273870",
#     "fills": [
#       {
#         "price": "2292.13000000",
#         "qty": "1.00000000",
#         "commission": "0.00000000",
#         "commissionAsset": "ETH",
#         "tradeId": "899916"
#       }
#     ],
#     "selfTradePreventionMode": "EXPIRE_MAKER"
#   },
#   "id": "6453418",
#   "clientOrderId": "x-R4BD3S824d5ed74de75f64119f9128",
#   "timestamp": 1703342273870,
#   "datetime": "2023-12-23T14:37:53.870Z",
#   "lastTradeTimestamp": 1703342273870,
#   "lastUpdateTimestamp": 1703342273870,
#   "symbol": "ETH/USDT",
#   "type": "market",
#   "timeInForce": "GTC",
#   "postOnly": false,
#   "reduceOnly": null,
#   "side": "buy",
#   "price": 2292.13,
#   "triggerPrice": null,
#   "amount": 1,
#   "cost": 2292.13,
#   "average": 2292.13,
#   "filled": 1,
#   "remaining": 0,
#   "status": "closed",
#   "fee": {
#     "currency": null,
#     "cost": null,
#     "rate": null
#   },
#   "trades": [
#     {
#       "info": {
#         "price": "2292.13000000",
#         "qty": "1.00000000",
#         "commission": "0.00000000",
#         "commissionAsset": "ETH",
#         "tradeId": "899916"
#       },
#       "timestamp": null,
#       "datetime": null,
#       "symbol": "ETH/USDT",
#       "id": "899916",
#       "order": null,
#       "type": null,
#       "side": null,
#       "takerOrMaker": null,
#       "price": 2292.13,
#       "amount": 1,
#       "cost": 2292.13,
#       "fee": {
#         "cost": 0,
#         "currency": "ETH"
#       },
#       "fees": [
#         {
#           "cost": "0.00000000",
#           "currency": "ETH"
#         }
#       ]
#     }
#   ],
#   "fees": [
#     {
#       "currency": null,
#       "cost": null,
#       "rate": null
#     }
#   ],
#   "stopPrice": null,
#   "takeProfitPrice": null,
#   "stopLossPrice": null
# }