from flask import jsonify
from opensky_api import StateVector
from app.models import Flight
from datetime import datetime, timedelta
import typing
import string
import random


def jsonify_vector(vector: StateVector):
    return jsonify(
        {'baro_altitude': vector.baro_altitude,
         'callsign': vector.callsign,
         'geo_altitude': vector.geo_altitude,
         'heading': vector.heading,
         'icao24': vector.icao24,
         'last_contact': vector.last_contact,
         'latitude': vector.latitude,
         'longitude': vector.longitude,
         'on_ground': vector.on_ground,
         'origin_country': vector.origin_country,
         'position_source': vector.position_source,
         'sensors': vector.sensors,
         'spi': vector.spi,
         'squawk': vector.squawk,
         'time_position': vector.time_position,
         'velocity': vector.velocity,
         'vertical_rate': vector.vertical_rate
         }
    )


def flight_number_parser(call_sign: str) -> (str, int):
    courier_request = call_sign[:2]
    number_request = int(call_sign[2:])

    return courier_request, number_request


def flight_retrieval(flight_request: dict, flight_int: typing.Optional[int] = 0) -> Flight:
    flight = flight_request["flights"][flight_int]

    flight_number = flight["airlineFsCode"] + flight["flightNumber"]
    flight_from = flight["departureAirportFsCode"]
    flight_to = flight["arrivalAirportFsCode"]

    scheduled_time_departure = datetime.strptime(flight["departureDate"], "%Y-%m-%dT%H:%M:%S.000")
    scheduled_time_arrival = datetime.strptime(flight["arrivalDate"], "%Y-%m-%dT%H:%M:%S.000")

    for airport in flight_request["appendix"]["airports"]:
        utc_delta = timedelta(hours=airport["utcOffsetHours"])
        if airport["fs"] == flight_from:
            scheduled_time_departure -= utc_delta
        elif airport["fs"] == flight_to:
            scheduled_time_arrival -= utc_delta

    airline = flight_request["appendix"]["airlines"][0]["name"]
    aircraft = flight["flightEquipmentIataCode"]

    flight_time = scheduled_time_departure - scheduled_time_arrival
    date = scheduled_time_departure.date()

    return Flight(flight_number=flight_number,
                  flight_from=flight_from,
                  flight_to=flight_to,
                  airline=airline,
                  aircraft=aircraft,
                  flight_time=int(flight_time.total_seconds()),
                  date=date,
                  scheduled_time_departure=scheduled_time_departure,
                  scheduled_time_arrival=scheduled_time_arrival)


def flights_exist(response: dict) -> bool:
    return len(response["flights"]) > 0


def generate_random_password(password_length: int = 8) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=password_length))