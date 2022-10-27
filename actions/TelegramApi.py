import requests

class TelegramAPI():
    def __init__(self):
        self.token = {BOT_TOKEN}
        self.url = f"https://api.telegram.org/bot{self.token}/"

    def sendMessage(self, chat_id, text, **kwargs):
        url = self.url + "sendMessage"

        params = {
            "chat_id": chat_id,
            "text": text,
        }

        for key, value in kwargs.items():
            params[key] = value
        
        r = requests.get(url, params = params)
        return r.json()
