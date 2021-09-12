from aviationstackWrapper import aviationstackApi
from app import db
from app.models import Flight
from datetime import datetime, timedelta


def fill_actual_time_task(flight_id, flight_date, courier, flight_number):
    req = aviationstackApi()
    req.add_app_credentials()
    req.add_flight_iata(courier=courier, number=flight_number)
    r = req.get()
    json_data = r.json()
    data = json_data["data"]
    print(data)

    for flight in data:
        if flight["flight_date"] == str(flight_date):
            db_flight = Flight.query.filter_by(id=flight_id).first()

            if (db_flight.scheduled_time_departure in ["", None]) or (db_flight.scheduled_time_arrival in ["", None]):
                db_flight.scheduled_time_departure = datetime.strptime(flight["departure"]["scheduled"],
                                                                       "%Y-%m-%dT%H:%M:%S%z") + timedelta(hours=1)
                db_flight.scheduled_time_arrival = datetime.strptime(flight["arrival"]["scheduled"],
                                                                     "%Y-%m-%dT%H:%M:%S%z") + timedelta(hours=1)
                td = db_flight.scheduled_time_arrival - db_flight.scheduled_time_departure
                db_flight.flight_time = datetime.strptime(str(td), "%H:%M:%S").time()

            if flight["flight_status"] == "landed":
                if (flight["arrival"]["actual"] not in ["", "null", None]) or \
                        (flight["departure"]["actual"] not in ["", "null", None]):
                    db_flight.actual_time_departure = datetime.strptime(flight["departure"]["actual"],
                                                                        "%Y-%m-%dT%H:%M:%S%z") + timedelta(hours=1)
                    db_flight.actual_time_arrival = datetime.strptime(flight["arrival"]["actual"],
                                                                      "%Y-%m-%dT%H:%M:%S%z") + timedelta(hours=1)
                    td = db_flight.actual_time_arrival - db_flight.actual_time_departure
                    db_flight.flight_time = datetime.strptime(str(td), "%H:%M:%S").time()

            db.session.add(db_flight)
            db.session.commit()

            break
