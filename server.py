from flask import Flask, jsonify, redirect, render_template, session, url_for
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
from werkzeug.exceptions import HTTPException
from functools import wraps
import configparser
import json
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


AUTH0_CALLBACK_URL = Config.conf.get('CONSTANTS', 'AUTH0_CALLBACK_URL')
AUTH0_CLIENT_ID = Config.conf.get('CONSTANTS', 'AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = Config.conf.get('CONSTANTS', 'AUTH0_CLIENT_SECRET')
AUTH0_DOMAIN = Config.conf.get('CONSTANTS', 'AUTH0_DOMAIN')
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = Config.conf.get('CONSTANTS', 'AUTH0_AUDIENCE')
EMAIL = Config.conf.get('CONSTANTS', 'EMAIL')


app = Flask(__name__)
app.secret_key = Config.conf.get('CONSTANTS', 'SECRET_KEY')

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL+'/oauth/token',
    authorize_url=AUTH0_BASE_URL+'/authorize',
    client_kwargs={
        'scope': EMAIL,
    },
)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            # Redirect to Login page here
            return redirect('/')
        return f(*args, **kwargs)

    return decorated


# Here we're using the /callback route.
@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/dashboard')


@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL)


@app.route('/dashboard')
@requires_auth
def dashboard():
    return render_template('dashboard.html',
                           userinfo=session['profile'],
                           userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))


@app.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('login', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


if __name__ == '__main__':
    app.run(debug=True)
