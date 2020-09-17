from flask import Flask, jsonify, redirect, render_template, session, url_for
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


@app.route('/')
def main():
    return "Working"


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


if __name__ == '__main__':
    app.run(debug=True)
