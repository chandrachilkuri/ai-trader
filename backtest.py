# Backtesting module for ai-trader
import yaml
from strategy import Strategy
from utils import compute_vwap, compute_atr, compute_rsi, is_volume_spike
import pandas as pd

def load_historical_data(symbol, path):
    # Load historical minute bars from CSV (exported from Alpaca)
    return pd.read_csv(path)

def run_backtest(config, symbol, data):
    strategy = Strategy(config)
    signals = []
    for i in range(config['strategy']['breakout_lookback'], len(data)):
        bars = data.iloc[i-config['strategy']['breakout_lookback']:i].to_dict('records')
        signal = strategy.generate_signal(symbol, bars)
        if signal:
            signals.append({'index': i, 'signal': signal, 'price': bars[-1]['close']})
    return signals

def main():
    config = yaml.safe_load(open('config.yml'))
    for symbol in config['watchlist']:
        data = load_historical_data(symbol, f'data/{symbol}_minute.csv')
        signals = run_backtest(config, symbol, data)
        print(f"Backtest for {symbol}: {signals}")

if __name__ == "__main__":
    main()

