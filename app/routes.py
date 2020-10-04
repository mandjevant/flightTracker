from flask import render_template, flash, redirect, url_for
from app import app, db, openskyAPI
from app.models import User, Flight
from app.forms import addFlightForm, editFlightForm, removeFlightForm
from app.appUtils import jsonify_vector, flight_number_parser, flights_exist, flight_retrieval
from app.flightstatsWrapper import flightStatsApi
import requests


@app.route('/')
def main():
    return "Working"


@app.route('/dashboard')
def dashboard():
    flights = Flight.query.all()
    return str([flight.flight_number for flight in flights])
    # return render_template("dashboard.html")


@app.route('/openskytest')
def opensky_test():
    states = openskyAPI.get_states()

    return jsonify_vector(states.states[0])


@app.route('/input', methods=['GET'])
def input_forms():
    add_form = addFlightForm()
    edit_form = editFlightForm()
    remove_form = removeFlightForm()

    return render_template("input.html", add_form=add_form, edit_form=edit_form, remove_form=remove_form)


@app.route('/add_form', methods=['GET', 'POST'])
def add_flight():
    add_form = addFlightForm()

    if add_form.validate_on_submit():
        courier, number = flight_number_parser(add_form.callSign.data)
        date = add_form.date.data

        req = flightStatsApi("https://api.flightstats.com/flex/flightFeatures")
        req.flight(courier, number, date.year, date.month, date.day)
        req.add_app_credentials()
        r = req.get()

        if not flights_exist(r.json()):
            flash("No flight found")
            return redirect(url_for('input_forms'))

        db.session.add(flight_retrieval(r.json()))
        db.session.commit()

    return redirect(url_for('input_forms'))


@app.route('/edit_form', methods=['POST'])
def edit_flight():
    edit_form = editFlightForm()

    if edit_form.validate_on_submit():
        flash("Editing!")

    return redirect(url_for('input_forms'))


@app.route('/remove_form', methods=['POST'])
def remove_flight():
    remove_form = removeFlightForm()

    if remove_form.validate_on_submit():
        flash("Removing!")

    return redirect(url_for('input_forms'))
