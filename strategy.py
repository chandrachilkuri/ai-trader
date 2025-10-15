# Signal logic for ai-trader
from utils import compute_vwap, compute_atr, compute_rsi, is_volume_spike

class Strategy:
    def __init__(self, config):
        self.config = config
    def generate_signal(self, symbol, data):
        # Compute indicators
        vwap = compute_vwap(data, self.config['thresholds']['vwap_window'])
        atr = compute_atr(data, self.config['thresholds']['atr_window'])
        rsi = compute_rsi(data, self.config['thresholds']['rsi_window'])
        volume_spike = is_volume_spike(data, self.config['thresholds']['volume_spike'])
        recent_high = max([bar['high'] for bar in data[-self.config['strategy']['breakout_lookback']:]])
        price = data[-1]['close']
        # BUY signal
        if price > recent_high and price > vwap and rsi > 50 and volume_spike:
            return 'BUY'
        # EXIT signal
        if price < vwap or price < (max([bar['close'] for bar in data[-self.config['strategy']['breakout_lookback']:]]) - self.config['strategy']['trailing_atr_mult'] * atr):
            return 'EXIT'
        return None

