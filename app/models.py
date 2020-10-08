from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(64), default="viewer")

    def __repr__(self) -> str:
        return f"<User {self.username}>"

    def set_password(self, password) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    def set_admin(self) -> None:
        self.role = "admin"

    def is_admin(self) -> bool:
        return self.role == "admin"


@login.user_loader
def load_user(user_id: int):
    return User.query.get(user_id)


class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flight_number = db.Column(db.VARCHAR)
    flight_from = db.Column(db.String)
    flight_to = db.Column(db.String)
    airline = db.Column(db.String)
    aircraft = db.Column(db.VARCHAR)
    flight_time = db.Column(db.INT)
    date = db.Column(db.Date)
    scheduled_time_departure = db.Column(db.DateTime)
    actual_time_departure = db.Column(db.DateTime)
    scheduled_time_arrival = db.Column(db.DateTime)
    actual_time_arrival = db.Column(db.DateTime)

    def __repr__(self) -> str:
        return f"<FlightNumber {self.flight_number}>"
