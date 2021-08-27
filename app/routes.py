import typing

from flask import render_template, flash, redirect, url_for, abort
from app import app, db
from app.models import User, Flight
from app.forms import addFlightForm, editFlightForm, removeFlightForm, addUserForm, upgradeUserForm, \
    searchFlightForm, downgradeUserForm, removeUserForm, loginForm, changePasswordForm
from app.appUtils import flight_number_parser, generate_random_password
from flask_login import current_user, login_user, logout_user, login_required
from functools import wraps
from sqlalchemy import func, desc


def admin_check() -> bool:
    return current_user.is_admin()


def find_flight(call_sign, date) -> typing.Optional[int]:
    courier, number = flight_number_parser(call_sign)
    flight_exists = db.session.query(Flight.id).filter_by(flight_number=number,
                                                          airline=courier.upper(),
                                                          date=date).scalar()
    return flight_exists


def admin_required(function):
    @wraps(function)
    def admin_check_wrapper(*args, **kwargs):
        if not admin_check():
            flash("You do not have permission to view that page.")
            abort(404)

        return function(*args, **kwargs)

    return admin_check_wrapper


@app.route("/all_results_temp", methods=["GET"])
@login_required
def all_results_temp():
    flights = Flight.query.all()
    return str([flight.flight_number for flight in flights])


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    change_password_form = changePasswordForm()

    return render_template("user.html", change_password_form=change_password_form)


@app.route("/change_password", methods=["POST"])
@login_required
def change_password():
    change_password_form = changePasswordForm()

    if change_password_form.validate_on_submit():
        active_user = User.query.filter_by(username=current_user.username).first()
        active_user.set_password(change_password_form.new_password.data)

        db.session.commit()

        flash("Password successfully changed!")

    return redirect(url_for("profile"))


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    top_ten_most_visited_destinations = \
        db.session.query(Flight.flight_to,
                         func.count(Flight.flight_to).label("visits")
                         ).group_by(Flight.flight_to).order_by(desc("visits")).limit(10).all()

    alter_top_destinations = \
        db.session.query(Flight.flight_to,
                         func.count(Flight.flight_to).label("visits")
                         ).group_by(Flight.flight_to).order_by("visits").limit(10).all()

    coming_flights = db.session.query(Flight.flight_to, Flight.date, Flight.flight_number).order_by(Flight.date).limit(
        20).all()

    normal_users = User.query.filter_by(role="viewer").order_by(User.username).all()
    admin_users = User.query.filter_by(role="admin").order_by(User.username).all()

    return render_template("dashboard.html",
                           top_ten_most_visited_destinations=top_ten_most_visited_destinations,
                           alter_top_destinations=alter_top_destinations,
                           coming_flights=coming_flights,
                           normal_users=normal_users,
                           admin_users=admin_users)


@app.route("/", methods=["GET"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    login_form = loginForm()

    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()

        if user is None or not user.check_password(login_form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))

        login_user(user, remember=login_form.remember_me.data)
        return redirect(url_for("dashboard"))

    return render_template("login.html", login_form=login_form)


@app.route("/logout")
@login_required
def logout():
    logout_user()

    return redirect(url_for("login"))


@app.route("/input", methods=["GET"])
@login_required
@admin_required
def input_forms():
    add_flight_form = addFlightForm()
    search_flight_form = searchFlightForm()
    remove_flight_form = removeFlightForm()
    add_user_form = addUserForm()
    upgrade_user_form = upgradeUserForm()
    downgrade_user_form = downgradeUserForm()
    remove_user_form = removeUserForm()

    return render_template("input.html",
                           add_flight_form=add_flight_form,
                           search_flight_form=search_flight_form,
                           remove_flight_form=remove_flight_form,
                           add_user_form=add_user_form,
                           upgrade_user_form=upgrade_user_form,
                           downgrade_user_form=downgrade_user_form,
                           remove_user_form=remove_user_form)


@app.route("/add_flight_form", methods=["GET", "POST"])
@login_required
@admin_required
def add_flight():
    add_flight_form = addFlightForm()

    if add_flight_form.validate_on_submit():
        courier, number = flight_number_parser(add_flight_form.callSign.data)
        date = add_flight_form.date.data
        departure_airport = add_flight_form.flightFrom.data
        arrival_airport = add_flight_form.flightTo.data
        aircraft = add_flight_form.aircraft.data

        db.session.add(Flight(flight_number=number,
                              airline=courier.upper(),
                              date=date,
                              flight_from=departure_airport,
                              flight_to=arrival_airport,
                              aircraft=aircraft))
        db.session.commit()

        flash("Flight added.")

    return redirect(url_for("input_forms"))


@app.route("/search_flight_form", methods=["GET", "POST"])
@login_required
@admin_required
def search_flight():
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
