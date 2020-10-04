from flask import Flask
from opensky_api import OpenSkyApi
from flask_sqlalchemy import SQLAlchemy
import configparser
import sys
import os


class Config:
    conf = None

    @staticmethod
    def initiate_config():
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
app.secret_key = Config.conf.get('CONSTANTS', 'SECRET_KEY')
openskyAPI = OpenSkyApi(username=Config.conf.get('OPENSKY', 'USERNAME'),
                        password=Config.conf.get('OPENSKY', 'PASSWORD'))

flightStatsAppID = Config.conf.get('FLIGHTSTATS', 'APP_ID')
flightStatsAppKey = Config.conf.get('FLIGHTSTATS', 'APP_KEY')

from app import routes, models, errors
