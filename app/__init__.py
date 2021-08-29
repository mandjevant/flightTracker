from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import configparser
import sys
import os


class Config:
    """
    Class for importing sensitive configuration variables
     from conf.ini
    """
    conf = None

    @staticmethod
    def initiate_config() -> bool:
        """
        Initiate configparser
         check if conf.ini can be found and read
        :return: conf.ini was found | bool
        """
        try:
            Config.conf = configparser.ConfigParser()
            if os.path.exists(os.getcwd() + '\\conf.ini'):
                Config.conf.read(os.getcwd() + '\\conf.ini')
            else:
                print("Config file, conf.ini, was not found.")
                return False

            return True

        except Exception as e:
            print("Could not initiate conf." + str(e))
            return False


if not Config.initiate_config():
    sys.exit()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                                    'flightTracker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app=app)
login = LoginManager(app=app)
login.login_view = "login"
app.secret_key = Config.conf.get('CONSTANTS', 'SECRET_KEY')

from app import routes, models, errors
