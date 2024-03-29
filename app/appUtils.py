from flask_login import current_user
from app import db
from app.models import Flight, Airport
import typing
import string
import random
import os


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


def admin_check() -> bool:
    """
    Check if current user is admin
    :return: if current user has admin role | bool
    """
    return current_user.is_admin()


def find_flight(call_sign, date) -> typing.Optional[int]:
    """
    Find a flight in the database
    :param call_sign: flight call sign
    :param date: date of flight
    :return: the flight id or None
    """
    courier, number = flight_number_parser(call_sign)
    flight_exists = db.session.query(Flight.id).filter_by(flight_number=number,
                                                          airline=courier.upper(),
                                                          date=date).scalar()
    return flight_exists


def _fill_flight(flight_a: Flight):
    """
    Fill flight database entry
     flight_from and flight_to
     from other database entries
     with identical flight number and airline
    :param flight_a: new db entry | Flight
    """
    flight_b = Flight.query.filter(Flight.id != flight_a.id,
                                   Flight.flight_number == flight_a.flight_number,
                                   Flight.airline == flight_a.airline,
                                   Flight.flight_from is not None,
                                   Flight.flight_to != "Destination...").first()

    if flight_b is not None:
        flight_a.flight_from = flight_b.flight_from
        flight_a.flight_to = flight_b.flight_to

        db.session.commit()


def find_airport(iata) -> typing.Optional[int]:
    """
    Find an airport in the database
    :param iata: airport iata
    :return: the airport id or None
    """
    airport_exists = db.session.query(Airport.id).filter_by(iata=iata).scalar()
    return airport_exists


def save_img(file, filename: str) -> str:
    """
    Save an image to ./static/images/airport_images folder
     return path
    :param file: image to save
    :param filename: name of image | str
    :return: path to image | str
    """
    file.save(os.path.join(os.path.dirname(__file__), f"static\\images\\airport_images\\{filename}"))

    return os.path.join(os.path.dirname(__file__), f"static\\images\\airport_images\\{filename}")
