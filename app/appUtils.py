import string
import random


def flight_number_parser(call_sign: str) -> (str, int):
    """
    Translates flight IATA to airline IATA and flight number
    :param call_sign: flight IATA / callsign | str
    :return: courier, flight number | (str, int)
    """
    courier_request = call_sign[:2]
    number_request = int(call_sign[2:])

    return courier_request, number_request


def generate_random_password(password_length: int = 8) -> str:
    """
    Generate random password
    :param password_length: password length | int
    :return: Random password | str
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=password_length))
