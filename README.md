# AI-Trader Discord Bot

## Features
- Streams real-time candlestick data (1min, 15min, 1h) for stocks using Twelve Data API
- News and sentiment analysis for tickers using NewsAPI and OpenAI GPT
- Discord bot responds to `/TICKER` commands (e.g., `/AAPL`) when tagged
- Upload an image with a ticker in your message for news/sentiment analysis
- Modular config for watchlist, strategy, and non-sensitive settings

## Setup
1. Clone the repo
2. Create a `.env` file in the project root with your API keys and Discord IDs:
   ```
   DISCORD_TOKEN=your_discord_token_here
   NEWSAPI_KEY=your_newsapi_key_here
   OPENAI_KEY=your_openai_key_here
   TWELVEDATA_KEY=your_twelvedata_key_here
   ALPACA_KEY_ID=your_alpaca_key_id_here
   ALPACA_SECRET_KEY=your_alpaca_secret_key_here
   ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here
   DISCORD_SERVER_ID=your_discord_server_id_here
   DISCORD_STOCKS_CHANNEL_ID=your_stocks_channel_id_here
   DISCORD_OPTIONS_CHANNEL_ID=your_options_channel_id_here
   DISCORD_FUTURES_CHANNEL_ID=your_futures_channel_id_here
   DISCORD_GENERAL_CHANNEL_ID=your_general_channel_id_here
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. `.env` is already in `.gitignore` (do not commit it)
5. Configure non-sensitive settings (watchlist, strategy, etc.) in `config.yml`. Channel IDs and server ID should be set in `.env` only (see comments in config.yml for guidance).
6. Run the bot:
   ```
   python3 main.py
   ```

## Usage
- Tag the bot in Discord and type `/AAPL` (or any ticker) in an allowed channel to get candlestick data
- Upload an image with a ticker in your message for news and sentiment analysis
- Use `!ping` to test bot connection

## Security
- All API keys, Discord IDs, and secrets are stored in `.env` and excluded from git
- Never commit your `.env` file to public repositories

## Extending
- Add more intervals, chart images, or trading logic as needed
- See code comments for modular extension points
