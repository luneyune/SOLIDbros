import requests

api_url = "https://domo-dev.profintel.ru/tg-bot/docs"

params = {}


response = requests.post(api_url, json=params)
print(response)