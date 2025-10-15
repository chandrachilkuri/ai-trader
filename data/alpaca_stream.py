# Streams minute bars from Alpaca IEX websocket
import asyncio
import websockets
import json

class AlpacaStream:
    def __init__(self, config):
        self.config = config
        self.symbols = config['watchlist']
        self.key_id = config['alpaca']['key_id']
        self.secret_key = config['alpaca']['secret_key']
    async def connect(self):
        url = 'wss://stream.data.alpaca.markets/v2/iex'
        async with websockets.connect(url) as ws:
            await ws.send(json.dumps({"action": "auth", "key": self.key_id, "secret": self.secret_key}))
            await ws.send(json.dumps({"action": "subscribe", "bars": self.symbols}))
            buffer = {symbol: [] for symbol in self.symbols}
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                if data.get('stream') == 'bar':
                    bar = data['data']
                    symbol = bar['S']
                    buffer[symbol].append(bar)
                    yield symbol, buffer[symbol]
    def run(self):
        return self.connect()

