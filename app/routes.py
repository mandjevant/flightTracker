from flask import render_template, flash, redirect, url_for, abort
from app import app, db, scheduler
from app.models import User, Flight, Airport
from app.forms import addFlightForm, editFlightForm, removeFlightForm, addUserForm, upgradeUserForm, \
    searchFlightForm, downgradeUserForm, removeUserForm, loginForm, changePasswordForm, changeLanguageForm, \
    addAirportForm, searchAirportForm, editAirportForm, supplementAirportForm, removeAirportForm
from app.appUtils import flight_number_parser, generate_random_password, admin_check, find_flight, find_airport, \
    save_img, _fill_flight
from app.tasks import fill_actual_time_task
from flask_login import current_user, login_user, logout_user, login_required
from functools import wraps
from sqlalchemy import func, desc, asc
from werkzeug.utils import secure_filename
import datetime
import json
import ast
import os


def admin_required(function):
    """
    Custom decorator
     for routes that require admin role
    """

    @wraps(function)
    def admin_check_wrapper(*args, **kwargs):
        """
        Verify that user has admin role
         if not, display 400 error page
        """
        if not admin_check():
            flash("You do not have permission to view that page.")
            abort(404)

        return function(*args, **kwargs)

    return admin_check_wrapper


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """
    User profile route
     including form for changing password
    """
    change_password_form = changePasswordForm()
    change_language_form = changeLanguageForm()

    return render_template("user.html",
                           change_password_form=change_password_form,
                           change_language_form=change_language_form)


@app.route("/change_password", methods=["POST"])
@login_required
def change_password():
    """
    Separate route for form handling
     change password form
     update database on validation and submit of form
    """
    change_password_form = changePasswordForm()

    if change_password_form.validate_on_submit():
        active_user = User.query.filter_by(username=current_user.username).first()
        active_user.set_password(change_password_form.new_password.data)

        db.session.commit()

        flash("Password successfully changed!" if current_user.language == "english" else "Hasło poprawnie zmienione!")

    return redirect(url_for("profile"))


@app.route("/change_language", methods=["POST"])
@login_required
def change_language():
    """
    Separate route for form handling
     change language form
     update database on validation and submit of form
    """
    change_language_form = changeLanguageForm()

    if change_language_form.validate_on_submit():
        active_user = User.query.filter_by(username=current_user.username).first()
        active_user.language = change_language_form.language.data

        db.session.add(active_user)
        db.session.commit()

        flash("Language successfully changed!" if current_user.language == "english" else "Pomyślnie zmieniono język!")

    return redirect(url_for("profile"))


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """
    Dashboard route
     including data for tables
    """
    coming_flights = db.session.query(Flight.flight_to,
                                      Flight.date,
                                      Flight.flight_number,
                                      Flight.scheduled_time_departure,
                                      Flight.scheduled_time_arrival,
                                      Flight.aircraft).order_by(Flight.date).limit(10).all()

    recently_visited = db.session.query(Flight.flight_to,
                                        Flight.date,
                                        Flight.flight_number,
                                        Flight.scheduled_time_departure,
                                        Flight.actual_time_departure,
                                        Flight.scheduled_time_arrival,
                                        Flight.actual_time_arrival,
                                        Flight.aircraft).filter(
        Flight.date < datetime.date.today()).order_by(Flight.date).limit(10).all()

    most_visisted = \
        db.session.query(Flight.flight_to,
                         func.count(Flight.flight_to).label("visits")
                         ).group_by(Flight.flight_to).order_by(desc("visits")).limit(10).all()

    least_visited = \
        db.session.query(Flight.flight_to,
                         func.count(Flight.flight_to).label("visits")
                         ).group_by(Flight.flight_to).order_by(asc("visits")).limit(10).all()

    longest_flight = db.session.query(Flight.flight_to,
                                      Flight.date,
                                      Flight.flight_time,
                                      Flight.aircraft).order_by(desc(Flight.flight_time)).limit(1).all()
    shortest_flight = db.session.query(Flight.flight_to,
                                       Flight.date,
                                       Flight.flight_time,
                                       Flight.aircraft).filter(
        Flight.flight_time > 0).order_by(asc(Flight.flight_time)).limit(1).all()

    normal_users = User.query.filter_by(role="viewer").order_by(User.username).all()
    admin_users = User.query.filter_by(role="admin").order_by(User.username).all()

    return render_template("dashboard.html",
                           coming_flights=coming_flights,
                           recently_visited=recently_visited,
                           most_visisted=most_visisted,
                           least_visited=least_visited,
                           longest_flight=longest_flight,
                           shortest_flight=shortest_flight,
                           normal_users=normal_users,
                           admin_users=admin_users)


@app.route("/", methods=["GET"])
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login route
     including form for login form
     log in the user
    """
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    login_form = loginForm()

    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()

        if user is None or not user.check_password(login_form.password.data):
            flash("Invalid username or password"
                  if current_user.language == "english" else "Nieprawidłowa nazwa użytkownika lub hasło")
            return redirect(url_for("login"))

        login_user(user, remember=login_form.remember_me.data)
        return redirect(url_for("dashboard"))

    return render_template("login.html", login_form=login_form)


@app.route("/logout")
@login_required
def logout():
    """
    Logout route
     for logging out the user
    """
    logout_user()

    return redirect(url_for("login"))


@app.route("/input", methods=["GET"])
@login_required
@admin_required
def input_forms():
    """
    Route for data input
     including all forms
    """
    add_flight_form = addFlightForm()
    search_flight_form = searchFlightForm()
    remove_flight_form = removeFlightForm()
    add_user_form = addUserForm()
    upgrade_user_form = upgradeUserForm()
    downgrade_user_form = downgradeUserForm()
    remove_user_form = removeUserForm()
    add_airport_form = addAirportForm()
    search_airport_form = searchAirportForm()
    remove_airport_form = removeAirportForm()

    return render_template("input.html",
                           add_flight_form=add_flight_form,
                           search_flight_form=search_flight_form,
                           remove_flight_form=remove_flight_form,
                           add_user_form=add_user_form,
                           upgrade_user_form=upgrade_user_form,
                           downgrade_user_form=downgrade_user_form,
                           remove_user_form=remove_user_form,
                           add_airport_form=add_airport_form,
                           search_airport_form=search_airport_form,
                           remove_airport_form=remove_airport_form)


@app.route("/add_flight_form", methods=["GET", "POST"])
@login_required
@admin_required
def add_flight():
    """
    Separate route for form handling
     add flight form
     update database on validation and submit of form
    """
    add_flight_form = addFlightForm()

    if add_flight_form.validate_on_submit():
        courier, number = flight_number_parser(add_flight_form.callSign.data)
        date = add_flight_form.date.data
        departure_airport = add_flight_form.flightFrom.data
        arrival_airport = add_flight_form.flightTo.data
        aircraft = add_flight_form.aircraft.data

        flight_a = Flight(flight_number=number,
                          airline=courier.upper(),
                          date=date,
                          flight_from=departure_airport,
                          flight_to=arrival_airport,
                          aircraft=aircraft)

        db.session.add(flight_a)
        db.session.commit()

        if date >= datetime.datetime.now().date():
            run_datetime = datetime.datetime.combine(date, (datetime.datetime.min +
                                                            datetime.timedelta(hours=13, minutes=57)).time())

        scheduler.add_job(
            func=fill_actual_time_task,
            trigger="date",
            run_date=run_datetime,
            id=f"Fill actual time task for {courier.upper()}{number}",
            kwargs={"flight_id": flight_a.id,
                    "flight_date": date,
                    "courier": courier.upper(),
                    "flight_number": number}
        )

        # fill_actual_time_task(flight_a.id, date, courier.upper(), number)

        if (departure_airport in ["", "None", None]) or (arrival_airport in ["", "None", None, "Destination..."]):
            _fill_flight(flight_a=flight_a)

        flash("Flight added.")

    return redirect(url_for("input_forms"))


@app.route("/search_flight_form", methods=["GET", "POST"])
@login_required
@admin_required
def search_flight():
    """
    Separate route for form handling
     search flight form
     verify if flight exists
     redirect to show flight page on validation and submit of form
    """
    search_flight_form = searchFlightForm()

    if search_flight_form.validate_on_submit():
        flight_exists = find_flight(search_flight_form.callSign.data, search_flight_form.date.data)

        if flight_exists is None:
            flash("Could not find flight.")
            return redirect(url_for("input_forms"))

        return redirect(url_for("show_flight", flight_id=flight_exists))

    return redirect(url_for("input_forms"))


@app.route("/show_flight/<int:flight_id>", methods=["GET", "POST"])
@login_required
@admin_required
def show_flight(flight_id: int):
    """
    Route for showing a flight
     including edit flight form
     set default dynamically
    :param flight_id: flight id | int
    """
    flight = Flight.query.filter_by(id=flight_id).first()
    edit_flight_form = editFlightForm()

    edit_flight_form.flightTo.data = flight.flight_to if flight.flight_to not in ["", None] else "Departure airport"
    edit_flight_form.flightFrom.data = flight.flight_from if flight.flight_from not in ["", None] \
        else "Arrival airport"
    edit_flight_form.aircraft.data = flight.aircraft if flight.aircraft not in ["", None] else "Boeing 737-800"

    return render_template("result.html", flight_id=flight_id, edit_flight_form=edit_flight_form, flight=flight)


@app.route("/edit_flight_form/<int:flight_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_flight(flight_id: int):
    """
    Separate route for form handling
     edit flight form
     update database on validation and submit of form
    :param flight_id: flight id | int
    """
    flight = Flight.query.filter_by(id=flight_id).first()

    edit_flight_form = editFlightForm()

    if edit_flight_form.validate_on_submit():
        flight.flight_to = edit_flight_form.flightTo.data
        flight.flight_from = edit_flight_form.flightFrom.data
        flight.aircraft = edit_flight_form.aircraft.data
        db.session.add(flight)
        db.session.commit()

        flash("Flight edited!")

    return redirect(url_for("show_flight", flight_id=flight_id))


@app.route("/remove_flight_form", methods=["GET", "POST"])
@login_required
@admin_required
def remove_flight():
    """
    Separate route for form handling
     remove flight form
     verify if flight exists
     update database on validation and submit of form
    """
    remove_flight_form = removeFlightForm()

    if remove_flight_form.validate_on_submit():
        flight_exists = find_flight(remove_flight_form.callSign.data, remove_flight_form.date.data)

        if flight_exists is None:
            flash("Could not find flight.")
            return redirect(url_for("input_forms"))

        courier, number = flight_number_parser(remove_flight_form.callSign.data)
        Flight.query.filter(Flight.id == flight_exists, Flight.flight_number == number,
                            Flight.airline == courier.upper(), Flight.date == remove_flight_form.date.data).delete()

        db.session.commit()

        flash("Flight removed.")

    return redirect(url_for("input_forms"))


@app.route("/add_user_form", methods=["GET", "POST"])
@login_required
@admin_required
def add_user():
    """
    Separate route for form handling
     add user form
     generate and display a random password
     update database on validation and submit of form
    """
    add_user_form = addUserForm()

    if add_user_form.validate_on_submit():
        new_user = User(username=add_user_form.username.data)

        if add_user_form.is_admin.data:
            new_user.set_admin()

        temp_pass = generate_random_password()
        new_user.set_password(temp_pass)

        db.session.add(new_user)
        db.session.commit()

        flash(f"User added.\nTheir temporary password is: \n{temp_pass}")

    return redirect(url_for("input_forms"))


@app.route("/upgrade_user_form", methods=["POST"])
@login_required
@admin_required
def upgrade_user():
    """
    Separate route for form handling
     upgrade user form
     update database on validation and submit of form
    """
    upgrade_user_form = upgradeUserForm()

    if upgrade_user_form.validate_on_submit():
        user_to_upgrade = User.query.filter_by(username=upgrade_user_form.username.data).first()
        user_to_upgrade.set_admin()

        db.session.commit()

        flash(f"{upgrade_user_form.username.data} is upgraded to an admin account.")

    return redirect(url_for("input_forms"))


@app.route("/downgrade_user_form", methods=["POST"])
@login_required
@admin_required
def downgrade_user():
    """
    Separate route for form handling
     downgrade user form
     update database on validation and submit of form
    """
    downgrade_user_form = downgradeUserForm()

    if downgrade_user_form.validate_on_submit():
        user_to_downgrade = User.query.filter_by(username=downgrade_user_form.username.data).first()
        user_to_downgrade.revoke_admin()

        db.session.commit()

        flash(f"{downgrade_user_form.username.data} is downgraded to a viewer account.")

    return redirect(url_for("input_forms"))


@app.route("/remove_user_form", methods=["POST"])
@login_required
@admin_required
def remove_user():
    """
    Separate route for form handling
     remove user form
     verify if user exists
     update database on validation and submit of form
    """
    remove_user_form = removeUserForm()

    if remove_user_form.validate_on_submit():
        user_exists = db.session.query(User.id).filter_by(username=remove_user_form.username.data).scalar()

        if user_exists is None:
            flash("Could not find user.")
            return redirect(url_for("input_forms"))

        User.query.filter(User.id == user_exists, User.username == remove_user_form.username.data).delete()

        db.session.commit()

        flash("User removed.")

    return redirect(url_for("input_forms"))


@app.route("/add_airport_form", methods=["GET", "POST"])
@login_required
@admin_required
def add_airport():
    """
    Separate route for form handling
     add airport form
     update database on validation and submit of form
    """
    add_airport_form = addAirportForm()

    if add_airport_form.validate_on_submit():
        name = add_airport_form.airport_name.data
        iata = add_airport_form.airport_iata.data.upper()
        city = add_airport_form.airport_city.data
        longitude = add_airport_form.airport_longitude.data
        latitude = add_airport_form.airport_latitude.data

        db.session.add(Airport(name=name,
                               iata=iata,
                               city=city,
                               longitude=longitude,
                               latitude=latitude))
        db.session.commit()

        flash("Airport added.")

    return redirect(url_for("input_forms"))


@app.route("/search_airport_form", methods=["GET", "POST"])
@login_required
@admin_required
def search_airport():
    """
    Separate route for form handling
     search airport form
     verify if airport exists
     redirect to show airport page on validation and submit of form
    """
    search_airport_form = searchAirportForm()

    if search_airport_form.validate_on_submit():
        airport_exists = find_airport(iata=search_airport_form.airport_iata.data.upper())

        if airport_exists is None:
            flash("Could not find flight.")
            return redirect(url_for("input_forms"))

        return redirect(url_for("show_airport", airport_id=airport_exists))

    return redirect(url_for("input_forms"))


@app.route("/show_airport/<int:airport_id>", methods=["GET", "POST"])
@login_required
@admin_required
def show_airport(airport_id: int):
    """
    Route for showing an airport
     including edit airport form
     set default dynamically
    :param airport_id: airport id | int
    """
    airport = Airport.query.filter_by(id=airport_id).first()
    edit_airport_form = editAirportForm()
    supplement_airport_form = supplementAirportForm()

    edit_airport_form.airport_iata.data = airport.iata.upper() if airport.iata not in ["", None] else "Airport IATA"
    edit_airport_form.airport_city.data = airport.city if airport.city not in ["", None] else "Airport city"
    edit_airport_form.airport_name.data = airport.name if airport.name not in ["", None] else "Airport name"
    edit_airport_form.airport_latitude.data = airport.latitude if airport.latitude not in ["", None] else "Latitude"
    edit_airport_form.airport_longitude.data = airport.longitude if airport.longitude not in ["", None] else "Longitude"

    return render_template("result.html",
                           airport_id=airport_id,
                           edit_airport_form=edit_airport_form,
                           supplement_airport_form=supplement_airport_form,
                           airport=airport)


@app.route("/edit_airport_form/<int:airport_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_airport(airport_id: int):
    """
    Separate route for form handling
     edit airport form
     update database on validation and submit of form
    :param airport_id: airport id | int
    """
    airport = Airport.query.filter_by(id=airport_id).first()
    edit_airport_form = editAirportForm()

    if edit_airport_form.validate_on_submit():
        airport.iata = edit_airport_form.airport_iata.data.upper()
        airport.name = edit_airport_form.airport_name.data
        airport.city = edit_airport_form.airport_city.data
        airport.latitude = edit_airport_form.airport_latitude.data
        airport.longitude = edit_airport_form.airport_longitude.data

        db.session.add(airport)
        db.session.commit()

        flash("Airport edited!")

    return redirect(url_for("show_airport", airport_id=airport_id))


@app.route("/supplement_airport_form/<int:airport_id>", methods=["GET", "POST"])
@login_required
@admin_required
def supplement_airport(airport_id: int):
    """
    Separate route for form handling
     supplement airport form
     update database on validation and submit of form
    :param airport_id: airport id | int
    """
    airport = Airport.query.filter_by(id=airport_id).first()
    image_list = ast.literal_eval(airport.images) if airport.images not in ["", None] else list()
    supplement_airport_form = supplementAirportForm()

    if supplement_airport_form.validate_on_submit():
        if not supplement_airport_form.pictures.data:
            return redirect(url_for("show_airport", airport_id=airport_id))

        for file in supplement_airport_form.pictures.data:
            file_name = secure_filename(file.filename)
            image_list.append(save_img(file, file_name))

        airport.images = str(image_list)
        db.session.add(airport)
        db.session.commit()

        flash("Images added!")

    return redirect(url_for("show_airport", airport_id=airport_id))


@app.route("/remove_airport_form", methods=["GET", "POST"])
@login_required
@admin_required
def remove_airport():
    """
    Separate route for form handling
     remove airport form
     verify if airport exists
     update database on validation and submit of form
    """
    remove_airport_form = removeAirportForm()

    if remove_airport_form.validate_on_submit():
        airport_exists = find_airport(remove_airport_form.airport_iata.data.upper())

        if airport_exists is None:
            flash("Could not find airport.")
            return redirect(url_for("input_forms"))

        airport = Airport.query.filter(Airport.id == airport_exists).first()
        images_list = ast.literal_eval(airport.images)
        for path in images_list:
            os.remove(path)

        Airport.query.filter(Airport.id == airport_exists).delete()
        db.session.commit()

        flash("Airport removed.")

    return redirect(url_for("input_forms"))


@app.route("/map", methods=["GET", "POST"])
@login_required
def interactive_map():
    """
    Interactive map route
    """
    airport_data = list()
    airport_q = db.session.query(Airport.id,
                                 Airport.name,
                                 Airport.iata,
                                 Airport.city,
                                 Airport.longitude,
                                 Airport.latitude).all()
    for row in airport_q:
        airport_data.append(row._asdict())

    return render_template("map.html", airport_data=json.dumps({'airports': airport_data}))


@app.route("/airport/<airport_iata>", methods=["GET", "POST"])
@login_required
def airport(airport_iata: str):
    """
    Airport route including pictures from airport
    :param airport_iata: airport IATA | str
    """
    airport = Airport.query.filter(Airport.iata == airport_iata.upper()).first()
    proc_images_list = None

    if airport.images not in ["", None]:
        images_list = ast.literal_eval(airport.images)
        proc_images_list = ["..\\" + i[i.find("static"):] for i in images_list]

    return render_template("airport.html", airport=airport, images_list=proc_images_list)
