import requests
token = "5353342440:AAFGwIOKJY3MqhG-zvEbEjIMv-fHciFrZJM"

def send_telegram(channel_id:str, text: str):
    global token
    url = "https://api.telegram.org/bot"
    url += token
    method = url + "/sendMessage"

    r = requests.post(method, data={"chat_id": channel_id, "text": text})
    