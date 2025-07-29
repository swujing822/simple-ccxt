import ccxt
import json

all_contracts = {}

for exchange_id in ccxt.exchanges:
    try:
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class({'enableRateLimit': True})

        if not exchange.has.get('fetchMarkets', False):
            continue

        print(f"🟡 正在加载 {exchange_id} ...")
        markets = exchange.load_markets()

        contracts = []
        for market in markets.values():
            if market.get('contract') is True:
                contracts.append({
                    'symbol': market['symbol'],
                    'type': market.get('type', ''),
                    'base': market.get('base', ''),
                    'quote': market.get('quote', ''),
                    'linear': market.get('linear'),
                    'inverse': market.get('inverse'),
                    'expiry': market.get('expiry'),  # 期货到期时间，swap 为 None
                })

        if contracts:
            all_contracts[exchange_id] = contracts
            print(f"✅ {exchange_id}: 共 {len(contracts)} 个合约")
    except Exception as e:
        print(f"❌ {exchange_id}: 加载失败 - {str(e)}")

# 保存到 JSON 文件
with open("contracts.json", "w", encoding="utf-8") as f:
    json.dump(all_contracts, f, indent=2, ensure_ascii=False)

print(f"\n✅ 所有支持合约的交易所已保存到 contracts.json（共 {len(all_contracts)} 个交易所）")
