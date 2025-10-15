import discord
import os
import requests
from discord.ext import commands
from data.options import get_options_suggestion
from discord_alerts import send_alert
import yaml
import re
import dotenv

dotenv.load_dotenv()

# Load config
config = yaml.safe_load(open('config.yml'))
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
OPENAI_KEY = os.getenv('OPENAI_KEY')
TWELVEDATA_KEY = os.getenv('TWELVEDATA_KEY')
CHANNELS = {
    'stocks': config['discord'].get('stocks_channel_id'),
    'options': config['discord'].get('options_channel_id'),
    'futures': config['discord'].get('futures_channel_id'),
}

TWELVEDATA_URL = 'https://api.twelvedata.com/time_series'

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Helper: Get news from NewsAPI
def get_news(ticker):
    url = f'https://newsapi.org/v2/everything?q={ticker}&apiKey={NEWSAPI_KEY}'
    resp = requests.get(url)
    articles = resp.json().get('articles', [])
    return articles[:5]  # Top 5 articles

# Helper: Get sentiment from ChatGPT
def get_sentiment_analysis(ticker, news):
    prompt = f"Analyze the sentiment and provide a summary for {ticker} based on the following news articles: {news}"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
    data = {"model": "gpt-4", "messages": [{"role": "user", "content": prompt}]}
    resp = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
    result = resp.json()
    return result['choices'][0]['message']['content'] if 'choices' in result else "No analysis available."

# Helper: Get candlestick data from Twelve Data

def get_candles(symbol, interval):
    params = {
        'symbol': symbol,
        'interval': interval,
        'outputsize': 100,
        'apikey': TWELVEDATA_KEY,
        'format': 'JSON'
    }
    resp = requests.get(TWELVEDATA_URL, params=params)
    data = resp.json()
    if 'values' in data:
        return data['values']
    else:
        return None

# Helper: Format candle summary

def format_candle_summary(candles, interval):
    if not candles:
        return f"No data found for interval {interval}."
    latest = candles[0]
    return (f"Interval: {interval}\n"
            f"Time: {latest['datetime']}\n"
            f"Open: {latest['open']}\n"
            f"High: {latest['high']}\n"
            f"Low: {latest['low']}\n"
            f"Close: {latest['close']}\n"
            f"Volume: {latest.get('volume', 'N/A')}")

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user} (ID: {bot.user.id})')

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.event
async def on_message(message):
    print(f"Received message in channel {message.channel.id}: {message.content}")
    if not message.guild or str(message.guild.id) != str(config['discord']['server_id']):
        print("Message not in target server.")
        await bot.process_commands(message)
        return
    allowed_channels = [
        str(config['discord'].get('stocks_channel_id', '')),
        str(config['discord'].get('options_channel_id', '')),
        str(config['discord'].get('futures_channel_id', '')),
        str(config['discord'].get('general_channel_id', ''))
    ]
    print(f"Allowed channels: {allowed_channels}")
    print(f"Incoming channel: {str(message.channel.id)}")
    if str(message.channel.id) not in allowed_channels:
        print("Message not in allowed channel.")
        await bot.process_commands(message)
        return
    # Check for /TICKER command when bot is tagged
    bot_tag_variants = [f'<@{bot.user.id}>', f'<@!{bot.user.id}>']
    content = message.content.strip()
    if any(content.startswith(tag) for tag in bot_tag_variants):
        # Remove bot tag from start
        for tag in bot_tag_variants:
            if content.startswith(tag):
                content = content[len(tag):].strip()
        # Match /TICKER (e.g., /AAPL)
        match = re.match(r'^/([A-Z]{1,5})$', content)
        if match:
            symbol = match.group(1)
            print(f"Detected ticker command: {symbol}")
            intervals = ['1min', '15min', '1h']
            summaries = []
            for interval in intervals:
                candles = get_candles(symbol, interval)
                print(f"Interval {interval} candles: {candles[:1] if candles else 'None'}")
                summaries.append(format_candle_summary(candles, interval))
            embed = discord.Embed(title=f"Candlestick Data for {symbol}")
            for summary in summaries:
                interval = summary.split('\n')[0].replace('Interval: ', '')
                embed.add_field(name=f"{interval} Candles", value=summary, inline=False)
            await message.channel.send(embed=embed)
            await bot.process_commands(message)
            return
        else:
            print("No valid /TICKER command detected after bot tag.")
    # Check for image upload
    if message.attachments:
        print("Detected image upload.")
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                ticker = None
                for word in message.content.split():
                    if word.isupper() and len(word) <= 5:
                        ticker = word
                        break
                if not ticker:
                    await message.channel.send("Please specify the ticker in your message.")
                    await bot.process_commands(message)
                    return
                print(f"Fetching news and sentiment for ticker: {ticker}")
                news = get_news(ticker)
                analysis = get_sentiment_analysis(ticker, news)
                embed = discord.Embed(title=f"Analysis for {ticker}", description=analysis)
                embed.add_field(name="Top News", value="\n".join([a['title'] for a in news]), inline=False)
                await message.channel.send(embed=embed)
    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
