import pandas as pd
import time

from strategy.base import BaseStrategy


class TriangularArbitrage(BaseStrategy):
	def calc(self):
		# 加载行情
		markets = self.exchange.load_markets()
		# 找到同时以A和B计价的交易对
		market_a = 'BTC'
		market_b = 'ETH'
		symbols = list(markets.keys())
		symbols_df = pd.DataFrame(symbols, columns=['symbol'])
		# 分割字符串得到 基础货币/计价货币
		base_quote_df = symbols_df['symbol'].str.split('/', expand=True)
		base_quote_df.columns = ['base', 'quote']
		# 过滤得到以 A B 计价的计价货币
		base_a_list = base_quote_df[base_quote_df['quote'] == market_a]['base'].tolist()
		base_b_list = base_quote_df[base_quote_df['quote'] == market_b]['base'].tolist()
		# 获取相同的基础货币列表
		common_base_list = list(set(base_a_list) & set(base_b_list))
		print('{}和{}的共同基础货币为:{}'.format(market_a, market_b, common_base_list))
		# 执行套利步骤
		columns = [
			'Market A',
			'Market B',
			'Market C',
			'P1',
			'P2',
			'P3',
			'Profit(‰)'
		]
		results_df = pd.DataFrame(columns=columns)
		# 获取行情
		for market_c in common_base_list:
			ba = market_b + '/' + market_a
			cb = market_c + '/' + market_b
			ca = market_c + '/' + market_a
			# 获取最新价格
			p1, p1_ts = self._fetch_ticker_safe(ba)
			p2, p2_ts = self._fetch_ticker_safe(cb)
			p3, p3_ts = self._fetch_ticker_safe(ca)
			if p1 == 0 or p2 == 0 or p3 == 0:
				continue
			print('p1_ts={}, p2_ts={}, p3_ts={}'.format(p1_ts, p2_ts, p3_ts))
			# 价差
			profit = (p3 / (p1 * p2) - 1) * 1000
			results_df.loc[len(results_df)] = {
				'Market A': market_a,
				'Market B': market_b,
				'Market C': market_c,
				'P1': p1,
				'P2': p2,
				'P3': p3,
				'Profit(‰)': profit,
			}
			# 打印这一行
			print(results_df.tail(1))
			# 防止超过rate limit
			time.sleep(self.exchange.rateLimit / 1000)
		# 最后把内容生成到csv
		results_df.to_csv('./tri_arb_result.csv', index=False)

	def trad(self):
		pass

	def _fetch_ticker_safe(self, symbol):
		try:
			ticker_data = self.exchange.fetch_ticker(symbol)
			return ticker_data['last'] or 0, ticker_data['timestamp'] or 0
		except Exception as e:
			return 0, 0


if __name__ == '__main__':
	TriangularArbitrage().calc()