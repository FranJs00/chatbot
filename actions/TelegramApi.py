import requests

class TelegramAPI():
    def __init__(self):
        self.token = "5672897381:AAHE_iiMCRd79V1_WJO-pI-2g0C9Qr7cAJc"
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
