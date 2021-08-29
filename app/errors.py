from flask import render_template
from app import app, db


@app.errorhandler(404)
def not_found_error(error):
    """
    Render error template
    :param error: error
    :return: 404 error page
    """
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    """
    Roll back database and render error template
    :param error: error
    :return: 500 error page
    """
    db.session.rollback()
    return render_template('500.html'), 500
