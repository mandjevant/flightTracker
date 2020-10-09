from flask import render_template, flash, redirect, url_for, abort
from app import app, db, openskyAPI
from app.models import User, Flight
from app.forms import addFlightForm, editFlightForm, removeFlightForm, addUserForm, upgradeUserForm, downgradeUserForm, \
    removeUserForm, loginForm
from app.appUtils import jsonify_vector, flight_number_parser, flights_exist, flight_retrieval, generate_random_password
from app.flightstatsWrapper import flightStatsApi
from flask_login import current_user, login_user, logout_user, login_required
from functools import wraps


def admin_check() -> bool:
    return current_user.is_admin()


def admin_required(func):
    @wraps(func)
    def admin_check_wrapper(*args, **kwargs):
        if not admin_check():
            flash("You do not have permission to view that page.")
            abort(404)

        return func(*args, **kwargs)

    return admin_check_wrapper


@app.route("/all_results_temp", methods=["GET"])
@login_required
def all_results_temp():
    flights = Flight.query.all()
    return str([flight.flight_number for flight in flights])


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return render_template("dashboard.html")


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


@app.route("/openskytest", methods=["GET"])
@login_required
def opensky_test():
    states = openskyAPI.get_states()

    return jsonify_vector(states.states[0])


@app.route("/input", methods=["GET"])
@login_required
@admin_required
def input_forms():
    add_flight_form = addFlightForm()
    edit_flight_form = editFlightForm()
    remove_flight_form = removeFlightForm()
    add_user_form = addUserForm()
    upgrade_user_form = upgradeUserForm()
    downgrade_user_form = downgradeUserForm()
    remove_user_form = removeUserForm()
    
    return render_template("input.html",
                           add_flight_form=add_flight_form,
                           edit_flight_form=edit_flight_form,
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

        req = flightStatsApi("https://api.flightstats.com/flex/flightFeatures")
        req.flight(courier, number, date.year, date.month, date.day)
        req.add_app_credentials()
        r = req.get()

        if not flights_exist(r.json()):
            flash("No flight found")
            return redirect(url_for("input_forms"))

        db.session.add(flight_retrieval(r.json()))
        db.session.commit()

        flash("Flight added.")

    return redirect(url_for("input_forms"))


@app.route("/edit_flight_form", methods=["POST"])
@login_required
@admin_required
def edit_flight():
    edit_flight_form = editFlightForm()

    if edit_flight_form.validate_on_submit():
        flash("Editing!")

    return redirect(url_for("input_forms"))


@app.route("/remove_flight_form", methods=["POST"])
@login_required
@admin_required
def remove_flight():
    remove_flight_form = removeFlightForm()

    if remove_flight_form.validate_on_submit():
        flight_exists = db.session.query(Flight.id).filter_by(flight_number=remove_flight_form.callSign.data,
                                                              date=remove_flight_form.date.data).scalar()
        if flight_exists is None:
            flash("Could not find flight.")
            return redirect(url_for("input_forms"))

        Flight.query.filter(Flight.id == flight_exists, Flight.flight_number == remove_flight_form.callSign.data,
                            Flight.date == remove_flight_form.date.data).delete()

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
