from flask import Flask, jsonify, request, render_template
from opensky_api import OpenSkyApi, StateVector
from app.forms import addFlightForm, editFlightForm, removeFlightForm
import configparser
import sys
import os


class Config:
    conf = None

    @staticmethod
    def initiate_config():
        try:
            Config.conf = configparser.ConfigParser()
            os.chdir(sys.path[0])
            if os.path.exists('conf.ini'):
                Config.conf.read('conf.ini')
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
app.secret_key = Config.conf.get('CONSTANTS', 'SECRET_KEY')
openskyAPI = OpenSkyApi(username=Config.conf.get('OPENSKY', 'USERNAME'),
                        password=Config.conf.get('OPENSKY', 'PASSWORD'))


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


@app.route('/')
def main():
    return "Working"


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


@app.route('/openskytest')
def opensky_test():
    states = openskyAPI.get_states()

    return jsonify_vector(states.states[0])


@app.route('/input', methods=['GET'])
def input_form():
    add_form = addFlightForm()
    edit_form = editFlightForm()
    remove_form = removeFlightForm()

    return render_template("input.html", add_form=add_form, edit_form=edit_form, remove_form=remove_form)


@app.route('/add_form', methods=['POST'])
def add_flight():
    add_form = addFlightForm()
    edit_form = editFlightForm()
    remove_form = removeFlightForm()

    if add_form.validate_on_submit():
        return 'adding!'

    return render_template("input.html", add_form=add_form, edit_form=edit_form, remove_form=remove_form)


@app.route('/edit_form', methods=['POST'])
def edit_flight():
    add_form = addFlightForm()
    edit_form = editFlightForm()
    remove_form = removeFlightForm()

    if edit_form.validate_on_submit():
        return 'editing!'

    return render_template("input.html", add_form=add_form, edit_form=edit_form, remove_form=remove_form)


@app.route('/remove_form', methods=['POST'])
def remove_flight():
    add_form = addFlightForm()
    edit_form = editFlightForm()
    remove_form = removeFlightForm()

    if remove_form.validate_on_submit():
        return 'removing!'

    return render_template("input.html", add_form=add_form, edit_form=edit_form, remove_form=remove_form)


if __name__ == '__main__':
    app.run(debug=True)
