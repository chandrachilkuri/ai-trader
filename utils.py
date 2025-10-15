# Helper functions for indicators
import numpy as np

def compute_vwap(data, window):
    # VWAP: sum(price * volume) / sum(volume) over window
    prices = np.array([bar['close'] for bar in data[-window:]])
    volumes = np.array([bar['volume'] for bar in data[-window:]])
    vwap = np.sum(prices * volumes) / np.sum(volumes) if np.sum(volumes) > 0 else prices[-1]
    return vwap

def compute_atr(data, window):
    # ATR: average of true range over window
    trs = []
    for i in range(-window, 0):
        high = data[i]['high']
        low = data[i]['low']
        prev_close = data[i-1]['close'] if i-1 >= -len(data) else data[i]['close']
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)
    return np.mean(trs) if trs else 0

def compute_rsi(data, window):
    # RSI: relative strength index
    closes = np.array([bar['close'] for bar in data[-window-1:]])
    deltas = np.diff(closes)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gains)
    avg_loss = np.mean(losses)
    rs = avg_gain / avg_loss if avg_loss > 0 else 0
    rsi = 100 - (100 / (1 + rs)) if avg_loss > 0 else 100
    return rsi

def is_volume_spike(data, threshold):
    # Detect volume spike: last bar volume > threshold * avg volume
    volumes = np.array([bar['volume'] for bar in data[:-1]])
    avg_vol = np.mean(volumes) if len(volumes) > 0 else 0
    last_vol = data[-1]['volume']
    return last_vol > threshold * avg_vol if avg_vol > 0 else False
# Entry point for ai-trader
import yaml
from strategy import Strategy
from data.alpaca_stream import AlpacaStream
from discord_alerts import send_alert
from data.options import get_options_suggestion
from unusual_whales import get_unusual_whales_info

# Load config
def load_config(path='config.yml'):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    stream = AlpacaStream(config)
    strategy = Strategy(config)
    for symbol, data in stream.run():
        signal = strategy.generate_signal(symbol, data)
        if signal:
            option = get_options_suggestion(symbol, config)
            uw_info = get_unusual_whales_info(symbol, config)
            send_alert(symbol, signal, option, uw_info, config)

if __name__ == "__main__":
    main()
