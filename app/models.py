from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    """
    User database model
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(64), default="viewer")

    def __repr__(self) -> str:
        """
        Represent user class object as string
        :return: string representation of user class | str
        """
        return f"<User {self.username}>"

    def set_password(self, password) -> None:
        """
        Add password to user
         by saving the password hash
        :param password: the password
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password) -> bool:
        """
        Verify if input password matches user password
        :return: if saved password matches input password | bool
        """
        return check_password_hash(self.password_hash, password)

    def set_admin(self) -> None:
        """
        Set user role to admin
        """
        self.role = "admin"

    def revoke_admin(self) -> None:
        """
        Set user role to viewer
        """
        self.role = "viewer"

    def is_admin(self) -> bool:
        """
        Check if user has admin role
        :return: if user has admin role | bool
        """
        return self.role == "admin"


@login.user_loader
def load_user(user_id: int):
    """
    Load the user
    :param user_id: id of user | int
    :return: user
    """
    return User.query.get(user_id)


class Flight(db.Model):
    """
    Flight database model
    """
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
        """
        Represent flight class object as string
        :return: string representation of flight class | str
        """
        return f"<FlightNumber {self.flight_number}>"


class Airport(db.Model):
    """
    Airport database model
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    iata = db.Column(db.VARCHAR)
    city = db.Column(db.String)
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    images = db.Column(db.String, nullable=True)

    def __repr__(self) -> str:
        """
        Represent airport class object as string
        :return: string representation of airport class | str
        """
        return f"<AirportIATA> {self.iata}"
