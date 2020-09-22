from flask import jsonify
from opensky_api import StateVector


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
