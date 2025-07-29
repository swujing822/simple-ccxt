import ccxt
import json
from collections import defaultdict


def fetch_all_contracts(save_path="contracts.json"):
    """
    遍历所有 ccxt 交易所，提取所有支持的合约交易对，并保存为 JSON。
    """
    all_contracts = {}

    for exchange_id in ccxt.exchanges:
        try:
            exchange_class = getattr(ccxt, exchange_id)
            exchange = exchange_class({'enableRateLimit': True})

            if not exchange.has.get('fetchMarkets', False):
                continue

            print(f"🟡 加载 {exchange_id} ...")
            markets = exchange.load_markets()

            contracts = []
            for market in markets.values():
                if market.get('contract') is True:
                    contracts.append({
                        "symbol": market["symbol"],
                        "type": market.get("type", ""),
                        "base": market.get("base", ""),
                        "quote": market.get("quote", ""),
                        "linear": market.get("linear"),
                        "inverse": market.get("inverse"),
                        "expiry": market.get("expiry")
                    })

            if contracts:
                all_contracts[exchange_id] = contracts
                print(f"✅ {exchange_id}: {len(contracts)} 个合约")
        except Exception as e:
            print(f"❌ {exchange_id} 加载失败: {str(e)}")

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(all_contracts, f, indent=2, ensure_ascii=False)
    print(f"\n✅ 合约数据已保存到 {save_path}")


def analyze_popular_contracts(input_path="contracts.json", output_path="popular_contracts.json", min_exchange_count=10):
    """
    分析哪些 symbol 被多个交易所支持，筛选出支持交易所数 >= min_exchange_count 的 symbol。
    """
    with open(input_path, "r", encoding="utf-8") as f:
        all_contracts = json.load(f)

    symbol_to_exchanges = defaultdict(list)

    for exchange, contracts in all_contracts.items():
        for market in contracts:
            symbol = market["symbol"]
            symbol_to_exchanges[symbol].append(exchange)

    popular_contracts = []
    for symbol, exchanges in symbol_to_exchanges.items():
        if len(exchanges) >= min_exchange_count:
            popular_contracts.append({
                "symbol": symbol,
                "count": len(exchanges),
                "exchanges": sorted(exchanges)
            })

    popular_contracts.sort(key=lambda x: x["count"], reverse=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(popular_contracts, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 支持交易所 >= {min_exchange_count} 的合约已保存到 {output_path}，共 {len(popular_contracts)} 个")


def transpose_to_exchange_symbol_matrix(input_path="popular_contracts.json", output_path="exchange_to_symbols.json"):
    """
    将 popular_contracts.json 转换为 exchange -> [symbols] 的结构，并保存为 JSON。
    """
    with open(input_path, "r", encoding="utf-8") as f:
        popular_contracts = json.load(f)

    exchange_to_symbols = defaultdict(list)

    for item in popular_contracts:
        symbol = item["symbol"]
        for exchange in item["exchanges"]:
            exchange_to_symbols[exchange].append(symbol)

    for exchange in exchange_to_symbols:
        exchange_to_symbols[exchange] = sorted(exchange_to_symbols[exchange])

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(exchange_to_symbols, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 转置矩阵已保存到 {output_path}，共 {len(exchange_to_symbols)} 个交易所")


# ✅ 示例入口
if __name__ == "__main__":
    fetch_all_contracts("contracts.json")
    analyze_popular_contracts("contracts.json", "popular_contracts.json", min_exchange_count=10)
    transpose_to_exchange_symbol_matrix("popular_contracts.json", "exchange_to_symbols.json")
