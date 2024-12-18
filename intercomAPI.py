import requests
import json

import config

class ValidationError(Exception):
    pass

class IntercomAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

    def check_tenant(self, phone_number):
        url = "https://domo-dev.profintel.ru/tg-bot/check-tenant"
        
        payload = json.dumps({
            "phone": phone_number
        })

        response = requests.request("POST", url, headers=self.headers, data=payload)
        res_data = response.json()

        if response.status_code == 200:
            return res_data["tenant_id"]
        else:
            raise ValidationError(f"No tenants for {phone_number}")
    
    def tenant_apartments(self, tenant_id):
        url = "https://domo-dev.profintel.ru/tg-bot/domo.apartment"

        params = {
            "tenant_id": tenant_id
        }

        response = requests.request("GET", url, headers=self.headers, params=params)
        res_data = response.json()

        if response.status_code == 200:
            locations = [(loc["id"], f"{loc["location"]["readable_address"]} кв. {loc["location"]["apartments_number"]}") for loc in res_data]
            return locations
        else:
            raise ValidationError(f"No apartments for {tenant_id}")

    def apartment_intercoms(self, apartment_id, tenant_id):
        url = f"https://domo-dev.profintel.ru/tg-bot/domo.apartment/{apartment_id}/domofon"

        params = {
            "tenant_id": tenant_id
        }

        response = requests.request("GET", url, headers=self.headers, params=params)
        res_data = response.json()

        if response.status_code == 200:
            intercoms = [(inter["id"], inter["name"]) for inter in res_data]
            return intercoms
        else:
            raise ValidationError(f"No intercoms for {apartment_id=}, {tenant_id=}")
    
    def open_intercom(self, intercom_id, tenant_id, door_id=0):
        url = f"https://domo-dev.profintel.ru/tg-bot/domo.domofon/{intercom_id}/open"

        params = {
            "tenant_id": tenant_id
        }

        payload = json.dumps({
            "door_id": door_id
        })

        response = requests.request("POST", url, headers=self.headers, params=params, data=payload)
        res_data = response.json()

        if response.status_code == 200:
            return True
        
        return False
    
    def intercom_image(self, intercom_id, tenant_id):
        url = f"https://domo-dev.profintel.ru/tg-bot/domo.domofon/urlsOnType"

        params = {
            "tenant_id": tenant_id
        }

        payload = json.dumps({
            "intercoms_id": [
                intercom_id
            ],
            "media_type": [
                "JPEG"
            ]
        })

        response = requests.request("POST", url, headers=self.headers, params=params, data=payload)
        res_data = response.json()
        if response.status_code == 200:
            return (res_data[0]["jpeg"], res_data[0]["alt_jpeg"])
        else:
            raise ValidationError(f"No JPEG for {intercom_id=}")
