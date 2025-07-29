import json
from collections import defaultdict

# 加载 popular_contracts.json
with open("popular_contracts.json", "r", encoding="utf-8") as f:
    popular_contracts = json.load(f)

# 构建 exchange -> [symbols] 映射
exchange_to_symbols = defaultdict(list)

for item in popular_contracts:
    symbol = item['symbol']
    for exchange in item['exchanges']:
        exchange_to_symbols[exchange].append(symbol)

# 可选：按 symbol 排序
for exchange in exchange_to_symbols:
    exchange_to_symbols[exchange] = sorted(exchange_to_symbols[exchange])

# 保存为 JSON 文件
with open("exchange_to_symbols.json", "w", encoding="utf-8") as f:
    json.dump(exchange_to_symbols, f, indent=2, ensure_ascii=False)

print(f"✅ 已保存交易所 -> 合约列表到 exchange_to_symbols.json，共 {len(exchange_to_symbols)} 个交易所")
