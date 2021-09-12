from app import aviationStackAccessKey
import requests


class aviationstackApi:
    """
    Wrapper class aviationstack API
    """

    def __init__(self, base_url: str = "http://api.aviationstack.com/v1/flights"):
        """
        Initiate class variables
        :param base_url: base url for aviationstack API | str
        """
        self.base_url = base_url
        self.URL = self.base_url

    def add_app_credentials(self):
        """
        Supplement base url with application credentials
        """
        self.URL += f"?access_key={aviationStackAccessKey}"

    def add_flight_iata(self, courier, number):
        """
        Supplement url with flight iata for querying
        :param courier: courier
        :param number: flight number
        """
        self.URL += f"&flight_iata={courier}{number}"

    def get(self):
        """
        Perform API get request
        :return: request
        """
        return requests.get(self.URL)
