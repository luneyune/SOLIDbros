import requests

api_url = "https://domo-dev.profintel.ru/tg-bot/docs"

params = {"phone": 79995647082}

response = requests.get(api_url, json=params)
print(response)