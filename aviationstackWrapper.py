from app import aviationStackAccessKey
import requests


class aviationstackApi:
    def __init__(self, base_url="http://api.aviationstack.com/v1/flights"):
        self.base_url = base_url
        self.URL = self.base_url

    def add_app_credentials(self):
        self.URL += f"?access_key={aviationStackAccessKey}"

    def add_flight_iata(self, courier, number):
        self.URL += f"&flight_iata={courier}{number}"

    def get(self):
        return requests.get(self.URL)
