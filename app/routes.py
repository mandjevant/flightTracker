from flask import render_template
from app import app, db, openskyAPI
from app.models import User, Flight
from app.forms import addFlightForm, editFlightForm, removeFlightForm
from app.appUtils import jsonify_vector


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
        flight = Flight(flight_number=add_form.callSign.data)
        db.session.add(flight)
        db.session.commit()

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
