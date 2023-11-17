import json
from datetime import datetime
from functools import partial

import pytz
from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from geopy import Photon
from geopy.exc import GeocoderUnavailable
from geopy.extra.rate_limiter import RateLimiter


def get_geocode():
    try:
        geolocator = Photon(user_agent="LerngruppenKarte", scheme="http")
        geocode_de = partial(geolocator.geocode, language="de")
        return RateLimiter(geocode_de, min_delay_seconds=3)
    except GeocoderUnavailable as e:
        print("Cannot update location. Geocoder is unavailable.", e)


db = SQLAlchemy()
app = Flask(__name__,
            static_folder='../static',
            template_folder='../templates',
            static_url_path='')
bootstrap = Bootstrap5(app)

app.config.from_file('config.json', load=json.load)

APP_TZ = pytz.timezone(app.config['TIMEZONE'])

geocode = get_geocode()


with app.app_context():
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .database import *
    db.create_all()
    db.session.commit()

    from .default_db import init_db
    init_db(db)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.template_filter('datetime')
def format_datetime(value, format="%d.%m.%Y %H:%M"):
    if value is None:
        return ""
    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f').strftime(format)
