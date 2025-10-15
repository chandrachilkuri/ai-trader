# Fetches options chains from Alpha Vantage, fallback to yfinance
import requests
import yfinance as yf
import numpy as np

def get_options_suggestion(symbol, config):
    # Try Alpha Vantage first
    try:
        url = f'https://www.alphavantage.co/query?function=OPTION_CHAIN&symbol={symbol}&apikey={config["alpha_vantage"]["api_key"]}'
        resp = requests.get(url)
        chain = resp.json()
        # Filter contracts
        contracts = []
        for expiry in chain.get('expirations', []):
            days = (np.datetime64(expiry) - np.datetime64('today')).astype(int)
            if days < config['options']['min_days']:
                continue
            for strike, option in chain.get('options', {}).get(expiry, {}).items():
                delta = option.get('delta', 0)
                oi = option.get('open_interest', 0)
                spread = abs(option.get('ask', 0) - option.get('bid', 0)) / option.get('mid', 1)
                if delta >= config['options']['min_delta'] and oi >= config['options']['min_oi'] and spread <= config['options']['max_spread']:
                    contracts.append({
                        'expiry': expiry,
                        'strike': strike,
                        'mid': option.get('mid', 0),
                        'delta': delta,
                        'iv': option.get('implied_volatility', 0),
                        'desc': f"{expiry} {strike} {option.get('type', '')}",
                        'price': option.get('mid', 0),
                        'timestamp': option.get('timestamp', '')
                    })
        if contracts:
            return sorted(contracts, key=lambda x: x['expiry'])[0]
    except Exception:
        # Fallback to yfinance
        ticker = yf.Ticker(symbol)
        expiries = ticker.options
        for expiry in expiries:
            if (np.datetime64(expiry) - np.datetime64('today')).astype(int) < config['options']['min_days']:
                continue
            chain = ticker.option_chain(expiry)
            for opt in chain.calls.itertuples():
                delta = getattr(opt, 'delta', 0)
                oi = getattr(opt, 'openInterest', 0)
                spread = abs(opt.ask - opt.bid) / opt.lastPrice if opt.lastPrice else 1
                if delta >= config['options']['min_delta'] and oi >= config['options']['min_oi'] and spread <= config['options']['max_spread']:
                    return {
                        'expiry': expiry,
                        'strike': opt.strike,
                        'mid': opt.lastPrice,
                        'delta': delta,
                        'iv': getattr(opt, 'impliedVolatility', 0),
                        'desc': f"{expiry} {opt.strike} CALL",
                        'price': opt.lastPrice,
                        'timestamp': ''
                    }
    return None
