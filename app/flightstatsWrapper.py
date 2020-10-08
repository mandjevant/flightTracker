from app import flightStatsAppKey, flightStatsAppID
import requests


class flightStatsApi:
    def __init__(self, base_url) -> None:
        self.URL = base_url

    def flight(self, courier, number, year, month, day) -> None:
        self.URL += f"/rest/v1/json/flight/{courier}/{number}/dep/{year}/{month}/{day}"

    def add_app_credentials(self) -> None:
        self.URL += f"?appId={flightStatsAppID}&appKey={flightStatsAppKey}"

    def get(self) -> requests.Response:
        return requests.get(self.URL)