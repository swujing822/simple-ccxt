import ccxt.pro as ccxt
import asyncio
from datetime import datetime
import csv
import os

# === 通用配置 ===
TIMEOUT_SECONDS = 300
FUNDING_RATE_INTERVAL = 10

# ✅ 你只需要配置 exchange_id、symbol、是否要资金费率
EXCHANGES_CONFIG = [
    {"exchange_id": "gateio", "symbol": "DFDVX/USDT", "include_funding": False},
    {"exchange_id": "gateio", "symbol": "DFDVX/USDT:USDT", "include_funding": True},
]


def log(msg: str):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}] {msg}")


def append_csv(filename: str, header: list, row: list):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(row)


async def watch_orderbook(exchange, exchange_id: str, symbol: str):
    filename = f'orderbook_{exchange_id}_{symbol.replace("/", "_").replace(":", "_")}.csv'
    while True:
        try:
            ob = await exchange.watch_order_book(symbol)
            best_bid = ob['bids'][0] if ob['bids'] else ['N/A', 'N/A']
            best_ask = ob['asks'][0] if ob['asks'] else ['N/A', 'N/A']
            log(f"📊 [{exchange_id}] {symbol} | Bid: {best_bid} | Ask: {best_ask}")
            append_csv(filename,
                       ['timestamp', 'exchange_id', 'symbol', 'bid_price', 'bid_qty', 'ask_price', 'ask_qty'],
                       [datetime.now().isoformat(), exchange_id, symbol,
                        best_bid[0], best_bid[1], best_ask[0], best_ask[1]])
        except Exception as e:
            log(f"🔴 [{exchange_id}] Orderbook error on {symbol}: {e}")
            await asyncio.sleep(1)


async def watch_trades(exchange, exchange_id: str, symbol: str):
    filename = f'trades_{exchange_id}_{symbol.replace("/", "_").replace(":", "_")}.csv'
    while True:
        try:
            trades = await exchange.watch_trades(symbol)
            for trade in trades:
                price = trade.get('price')
                amount = trade.get('amount')
                side = trade.get('side', '').upper()
                log(f"💥 [{exchange_id}] {symbol} Trade: {side} @ {price} x {amount}")
                append_csv(filename,
                           ['timestamp', 'exchange_id', 'symbol', 'side', 'price', 'amount'],
                           [datetime.now().isoformat(), exchange_id, symbol, side, price, amount])
        except Exception as e:
            log(f"🔴 [{exchange_id}] Trade error on {symbol}: {e}")
            await asyncio.sleep(1)


async def poll_funding_rate(exchange, exchange_id: str, symbol: str):
    filename = f'funding_{exchange_id}_{symbol.replace("/", "_").replace(":", "_")}.csv'
    while True:
        try:
            funding = await exchange.fetch_funding_rate(symbol)
            mark = funding.get("markPrice")
            rate = funding.get("fundingRate")
            next_ts = funding.get("nextFundingTime")
            next_time = datetime.utcfromtimestamp(next_ts / 1000).strftime('%Y-%m-%d %H:%M:%S') if next_ts else "N/A"
            log(f"💸 [{exchange_id}] {symbol} Funding Rate: {rate:.6%} | Mark Price: {mark} | Next: {next_time}")
            append_csv(filename,
                       ['timestamp', 'exchange_id', 'symbol', 'funding_rate', 'mark_price', 'next_funding_time'],
                       [datetime.now().isoformat(), exchange_id, symbol, rate, mark, next_time])
        except Exception as e:
            log(f"🔴 [{exchange_id}] Funding rate error: {e}")
        await asyncio.sleep(FUNDING_RATE_INTERVAL)


async def subscribe_symbol(exchange, exchange_id: str, symbol: str, include_funding=False):
    tasks = [
        asyncio.create_task(watch_orderbook(exchange, exchange_id, symbol)),
        asyncio.create_task(watch_trades(exchange, exchange_id, symbol)),
    ]
    if include_funding:
        tasks.append(asyncio.create_task(poll_funding_rate(exchange, exchange_id, symbol)))
    return tasks


async def run():
    tasks = []
    exchange_instances = []

    for conf in EXCHANGES_CONFIG:
        try:
            exchange_id = conf["exchange_id"]
            symbol = conf["symbol"]
            include_funding = conf.get("include_funding", False)

            # 自动识别合约类
            exchange_class = getattr(ccxt, exchange_id)
            is_contract = ':' in symbol or include_funding
            params = {"options": {"defaultType": "future"}} if is_contract else {}

            exchange = exchange_class(params)
            exchange_instances.append(exchange)

            tasks += await subscribe_symbol(exchange, exchange_id, symbol, include_funding)
        except Exception as e:
            log(f"❌ 初始化失败: {conf['exchange_id']} - {e}")

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        log("🔴 所有任务被取消")
    except Exception as e:
        log(f"⚠️ 未处理异常: {e}")
    finally:
        for exchange in exchange_instances:
            await exchange.close()
        log("✅ 所有 exchange 资源已释放")


if __name__ == "__main__":
    try:
        log("🚀 启动行情 + 成交 + 资金费率订阅任务...")
        asyncio.run(asyncio.wait_for(run(), timeout=TIMEOUT_SECONDS))
    except asyncio.TimeoutError:
        log(f"⏰ 超时退出：运行超过 {TIMEOUT_SECONDS} 秒")
    except KeyboardInterrupt:
        log("🔴 手动中断退出")
