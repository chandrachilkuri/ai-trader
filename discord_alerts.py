# Sends rich Discord embed alerts
import requests

def send_alert(symbol, signal, option, uw_info, config):
    webhook_url = config['discord']['webhook_url']
    embed = {
        "title": f"{signal} Signal for {symbol}",
        "description": f"Price: {option.get('price', 'N/A')}\nOption: {option.get('desc', 'N/A')}\nUnusual Whales: {uw_info}",
        "timestamp": option.get('timestamp', ''),
        "fields": [
            {"name": "Expiry", "value": option.get('expiry', 'N/A')},
            {"name": "Strike", "value": option.get('strike', 'N/A')},
            {"name": "Delta", "value": option.get('delta', 'N/A')},
            {"name": "IV", "value": option.get('iv', 'N/A')},
        ]
    }
    requests.post(webhook_url, json={"embeds": [embed]})

