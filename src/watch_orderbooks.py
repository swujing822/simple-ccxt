import ccxt.pro as ccxtpro
import asyncio
import csv
import os
import time
from datetime import datetime, timezone
import shutil
from utils.save_csv import *
import json
from collections import defaultdict

from cache_writer import cache_orderbook_top2, periodic_cache_writer, flush_cache_to_csv

csv_dir = "../csv_orderbooks_exchange"

clean_dir(csv_dir)

csv_symbol_dir = "../csv_orderbooks_symbol"

clean_dir(csv_symbol_dir)


def transpose_to_exchange_symbol_matrix(start, end, input_path="seletor_pro/popular_contracts.json", output_path="exchange_to_symbols.json"):
    """
    将 popular_contracts.json 转换为 exchange -> [symbols] 的结构，并保存为 JSON。
    """
    with open(input_path, "r", encoding="utf-8") as f:
        popular_contracts = json.load(f)

    exchange_to_symbols = defaultdict(list)

    print("总个数:", len(popular_contracts))

    start = max(0, start)
    end = min(len(popular_contracts) -1 , end)

    print("本次执行: ", start, end, "共", end-start+1)

    for item in popular_contracts[start:end]:
        symbol = item["symbol"]

        for exchange in item["exchanges"]:
            exchange_to_symbols[exchange].append(symbol)

    for exchange in exchange_to_symbols:
        exchange_to_symbols[exchange] = sorted(exchange_to_symbols[exchange])

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(exchange_to_symbols, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 转置矩阵已保存到 {output_path}，共 {len(exchange_to_symbols)} 个交易所")

    return popular_contracts



async def watch_one_symbol(exchange, exchange_id, symbol, max_retries=3):
    retry_count = 0
    while retry_count < max_retries:
        try:
            ob = await exchange.watch_order_book(symbol)
            retry_count = 0  # 成功订阅后重置重试计数器
            cache_orderbook_top2(exchange_id, ob)
            cache_orderbook_top2(exchange_id, ob)

            # symbol_clean = symbol.replace("/", "_").replace(":", "_")
            # csv_file = f'{csv_dir}/inner_orderbook_{exchange_id}_{symbol_clean}.csv'
            # timestamp_ms = ob['timestamp']

            # save_orderbook_top2_to_csv(exchange_id, ob, csv_file)


            # csv_symbol_file = f'{csv_symbol_dir}/ob_{symbol_clean}.csv'
            # save_orderbook_top2_to_csv(exchange_id, ob, csv_symbol_file)
        except Exception as e:
            retry_count += 1
            print(f"🔴 Failed to subscribe {symbol} on {exchange_id}: {e} [retry {retry_count}/{max_retries}]")
            await asyncio.sleep(1)

    print(f"❌ Exiting {exchange_id} - {symbol} subscription after {max_retries} failed attempts.")

# 单个交易所聚合 ticker 订阅协程
async def watch_orderbooks(exchange_id, symbols):
    exchange_class = getattr(ccxtpro, exchange_id)
    exchange = exchange_class({'enableRateLimit': False})
    await exchange.load_markets()  # 必须加载市场

    try:
        if exchange.has['watchOrderBookForSymbols']:
            while True:
                ob = await exchange.watchOrderBookForSymbols(symbols)
                cache_orderbook_top2(exchange_id, ob)
                cache_orderbook_top2(exchange_id, ob)

                # symbol = ob['symbol'].replace("/", "_").replace(":", "_")
                # csv_file = f'{csv_dir}/orderbook_{exchange_id}_{symbol}.csv'

                # print(ob['asks'][0], ob['symbol'])
                # save_orderbook_top2_to_csv(exchange_id, ob, csv_file)

                # csv_symbol_file = f'{csv_symbol_dir}/ob_{symbol}.csv'
                # save_orderbook_top2_to_csv(exchange_id, ob, csv_symbol_file)
                # for symbol, ticker in tickers.items():
                #     save_ticker_to_csv(exchange_id, symbol, ticker)
        else:
            print(f"🟡 {exchange_id} does not support watchOrderBookForSymbols, skipping")
            # inner_tasks = []

            # for symbol in symbols:
            #     # tasks.append(asyncio.create_task(watch_orderbook(exchange_id, symbol)))
            #     print("inner start ", symbol)
            #     task = asyncio.create_task(watch_one_symbol(exchange, exchange_id, symbol))
            #     inner_tasks.append(task)
            #     await asyncio.sleep(1)  # 👈 延迟启动，避免被限速封 IP 等问题
            # try:
            #     await asyncio.gather(*inner_tasks)
            # except KeyboardInterrupt:
            #     print("\n🔴 Ctrl+C received. Cancelling tasks...")
            #     for task in inner_tasks:
            #         task.cancel()
            #     await asyncio.gather(*inner_tasks, return_exceptions=True)
    except asyncio.CancelledError:
        print(f"🟡 Cancelled: {exchange_id}")
    except Exception as e:
        print(f"🔴 Error in {exchange_id}: {e}")
    finally:
        await exchange.close()
        print(f"✅ Closed {exchange_id}")

import json
async def main():

    with open("./exchange_to_symbols.json", "r", encoding="utf-8") as f:
        ex_syms = json.load(f)

    with open("./exchange_profile.json", "r", encoding="utf-8") as f:
        exchange_profile = json.load(f)

    tasks = []
    # skips = ["digifinex", "bitmart", 'lbank', 'bitrue']
    skips = []

    # selected = ["ascendex", 'bybit']
    selected = ["ascendex"]
    exchanges = []

    for exchange_id in ex_syms:
        if exchange_id in skips:
            print("skip ", exchange_id)
            continue
        # if exchange_id not in selected:
        #     print("skip ", exchange_id)
        #     continue
                
        symbols = ex_syms[exchange_id]
        if exchange_id not in exchange_profile:
            print(f"key: {exchange_id} not exist.")
            continue
        elif not exchange_profile[exchange_id]['has_orderbooks']:
            print("no has_orderbooks" , exchange_id)
            try:
                exchange_class = getattr(ccxtpro, exchange_id)
                exchange = exchange_class({'enableRateLimit': False})
                await exchange.load_markets()  # 必须加载市场
                exchanges.append(exchange)
                for symbol in symbols:
                    print("inner start ", exchange_id, symbol, '...')

                    task = asyncio.create_task(watch_one_symbol(exchange, exchange_id, symbol))
                    tasks.append(task)
                    # await asyncio.sleep(2)
            except asyncio.CancelledError:
                print(f"🟡 Cancelled: {exchange_id}")
            except Exception as e:
                print(f"🔴 Error in {exchange_id}: {e}")
            finally:
                await exchange.close()
                print(f"✅ Closed {exchange_id}")
        else:
            print(f"start {exchange_id} >>>>>>>>>>>>>>>")
            task = asyncio.create_task(watch_orderbooks(exchange_id, symbols))
            tasks.append(task)
            await asyncio.sleep(1)  # 👈 延迟启动，避免被限速封 IP 等问题
    try:
        # await asyncio.gather(*tasks)
        # 添加定时任务
        flush_task = asyncio.create_task(periodic_cache_writer(cache_seconds))  # 每 1800 秒写入一次
        tasks.append(flush_task)

        await asyncio.gather(*tasks, return_exceptions=True)

    except KeyboardInterrupt:
        print("\n🔴 Ctrl+C received. Cancelling tasks...")
        # for ex in exchanges:
        #     print("111111111 close ", ex)

        #     ex.close()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        print("✅ All connections closed.")
    finally:
        for ex in exchanges:
            print("222222222 close ", ex)
            await ex.close()
            print(f"✅ Closed {ex}")

if __name__ == '__main__':
    # select_symbols = ["BTC/USDT:USDT","ETH/USDT:USDT","SOL/USDT:USDT","XRP/USDT:USDT","LTC/USDT:USDT",]
    # select_symbols = ["BTC/USDT:USDT"]

    start = 0
    end = 50
    cache_seconds = 60*30
    run_seconds = 60*60*2

    popular_contracts = transpose_to_exchange_symbol_matrix(start, end)

    # asyncio.run(main())

    try:
        # 设置 5 分钟（300 秒）超时
        asyncio.run(asyncio.wait_for(main(), timeout=run_seconds))
        
    except asyncio.TimeoutError:
        print("⏰ 超时退出：已经运行 5 分钟，正在清理任务并退出。")
    except KeyboardInterrupt:
        print("🔴 手动中断退出。")
    finally:
        # 手动调用 asyncio.run(main()) 之外的收尾清理（如有）
        flush_cache_to_csv()
        print("contracts 共有: ",len(popular_contracts), '本次执行：', start, end)
        print("🧹 清理结束，程序退出。")

