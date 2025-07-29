import json
from collections import defaultdict

supported_exchange_num = 10 # 过滤支持交易所数 >=10 的 symbol，并按数量排序

# 读取 contracts.json
with open("contracts.json", "r", encoding="utf-8") as f:
    all_contracts = json.load(f)

# 构建 symbol -> exchanges 映射
symbol_to_exchanges = defaultdict(list)

for exchange, contracts in all_contracts.items():
    for market in contracts:
        symbol = market['symbol']
        symbol_to_exchanges[symbol].append(exchange)

# 过滤支持交易所数 >=10 的 symbol，并按数量排序
popular_contracts = []
for symbol, exchanges in symbol_to_exchanges.items():
    if len(exchanges) >= supported_exchange_num:
        popular_contracts.append({
            "symbol": symbol,
            "count": len(exchanges),
            "exchanges": sorted(exchanges)
        })

# 按交易所支持数量降序排列
popular_contracts.sort(key=lambda x: x['count'], reverse=True)

# 保存为 popular_contracts.json
with open("popular_contracts.json", "w", encoding="utf-8") as f:
    json.dump(popular_contracts, f, indent=2, ensure_ascii=False)

print(f"✅ 已保存支持交易所 ≥{supported_exchange_num} 的热门合约到 popular_contracts.json，共 {len(popular_contracts)} 个")
