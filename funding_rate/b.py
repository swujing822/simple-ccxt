import ccxt



exchange = ccxt.lbank({
    'options': {
        'defaultType': 'future'  # 关键！加载 futures 合约而不是现货
    }
})

# 加载市场数据
markets = exchange.load_markets()

# 打印部分市场信息（键是交易对名）
# for symbol in markets:
#     market = markets[symbol]
#     if market.get('contract', False):  # 如果是合约
#         print(f"{symbol} | type: {market['type']} | contractSize: {market['contractSize']}")


# 加载市场
markets = exchange.load_markets()

# 查看 BNKR/USDT 是否存在
symbol = 'BNKR/USDT'
if symbol not in markets:
    raise Exception("Symbol not found in LBank")

# # 获取1分钟K线数据
ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=100)
# print(ohlcv)

import ccxt

exchange = ccxt.lbank()
print(exchange.has)


# # 转换为 pandas 表格
# df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
# df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')

# print(df.tail())
