from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flight_number = db.Column(db.VARCHAR)
    flight_from = db.Column(db.String)
    flight_to = db.Column(db.String)
    airline = db.Column(db.String)
    aircraft = db.Column(db.VARCHAR)
    flight_time = db.Column(db.Time)
    date = db.Column(db.Date)
    scheduled_time_departure = db.Column(db.Time)
    actual_time_departure = db.Column(db.Time)
    scheduled_time_arrival = db.Column(db.Time)
    actual_time_arrival = db.Column(db.Time)

    def __repr__(self):
        return f"<FlightNumber {self.flight_number}>"
