import csv
import os
from collections import defaultdict
from datetime import datetime, timezone
import asyncio
import time

# 用于存储缓存数据：键是文件路径，值是行列表
orderbook_cache = defaultdict(list)

def format_time_from_timestamp(ts):
    dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return dt.strftime('%H:%M:%S.') + f'{int(dt.microsecond / 1000):03d}'

def cache_orderbook_top2(exchange_id, ob):
    if ob.get('timestamp') is None:
        timestamp_ms = int(time.time() * 1000)
    else:
        timestamp_ms = ob['timestamp']

    bids = ob.get('bids', [])
    asks = ob.get('asks', [])
    formatted_time = format_time_from_timestamp(timestamp_ms)

    row = [
        timestamp_ms,
        formatted_time,
        exchange_id,
        ob.get('symbol'),
        bids[0][0] if len(bids) > 0 else None,
        bids[0][1] if len(bids) > 0 else None,
        bids[1][0] if len(bids) > 1 else None,
        bids[1][1] if len(bids) > 1 else None,
        asks[0][0] if len(asks) > 0 else None,
        asks[0][1] if len(asks) > 0 else None,
        asks[1][0] if len(asks) > 1 else None,
        asks[1][1] if len(asks) > 1 else None,
    ]

    symbol_clean = ob.get("symbol").replace("/", "_").replace(":", "_")
    path1 = f'../csv_orderbooks_exchange/orderbook_{exchange_id}_{symbol_clean}.csv'
    path2 = f'../csv_orderbooks_symbol/ob_{symbol_clean}.csv'

    orderbook_cache[path1].append(row)
    orderbook_cache[path2].append(row)

def flush_cache_to_csv():
    print("从缓存写入csv...")
    for csv_file, rows in orderbook_cache.items():
        if not rows:
            continue
        write_header = not os.path.exists(csv_file)
        with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow([
                    'timestamp', 'time', 'exchange', 'symbol',
                    'bid1_price', 'bid1_volume',
                    'bid2_price', 'bid2_volume',
                    'ask1_price', 'ask1_volume',
                    'ask2_price', 'ask2_volume'
                ])
            writer.writerows(rows)
    print(f"✅ 已写入 {len(orderbook_cache)} 个文件，总行数：{sum(len(v) for v in orderbook_cache.values())}")
    orderbook_cache.clear()

async def periodic_cache_writer(interval_sec=1800):
    while True:
        await asyncio.sleep(interval_sec)
        print(f"\n🧹 {datetime.now().isoformat()} 触发定时写入缓存到 CSV...")
        flush_cache_to_csv()
