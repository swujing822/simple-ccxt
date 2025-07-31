import ccxt
import pandas as pd
import matplotlib.pyplot as plt

def fetch_ohlcv(exchange, symbol, timeframe='1m', limit=100):
    # 获取K线
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df[['time', 'close']]

def main():
    limit = 100
    timeframe = '1m'
    spot_symbol = 'BNKR/USDT'          # LBank现货
    futures_symbol = 'BNKR/USDT:USDT'  # LBank永续合约，具体看交易所文档和ccxt支持情况

    exchange = ccxt.lbank({
        'enableRateLimit': True,
    })

    print('Fetching spot data...')
    spot_df = fetch_ohlcv(exchange, spot_symbol, timeframe, limit)
    print('Fetching futures data...')
    try:
        futures_df = fetch_ohlcv(exchange, futures_symbol, timeframe, limit)
    except Exception as e:
        print(f'获取合约数据失败: {e}')
        return

    # 时间对齐
    spot_df.set_index('time', inplace=True)
    futures_df.set_index('time', inplace=True)
    df = spot_df.join(futures_df, lsuffix='_spot', rsuffix='_futures', how='inner')
    df['basis_percent'] = (df['close_futures'] - df['close_spot']) / df['close_spot'] * 100
    df.reset_index(inplace=True)

    # 画图
    fig, ax1 = plt.subplots(figsize=(14,7))
    ax1.plot(df['time'], df['close_spot'], label='现货价格', color='blue', linestyle='-')
    ax1.plot(df['time'], df['close_futures'], label='永续合约价格', color='red', linestyle='-')
    ax1.set_xlabel('时间')
    ax1.set_ylabel('价格 (USDT)')
    ax1.legend(loc='upper left')

    ax2 = ax1.twinx()
    ax2.plot(df['time'], df['basis_percent'], label='基差百分比(%)', color='green', linestyle='-')
    ax2.set_ylabel('基差百分比 (%)')
    ax2.legend(loc='upper right')

    plt.title(f'{spot_symbol} 现货 vs 永续合约价格 + 基差百分比')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

main()