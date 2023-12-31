import json

import pytz
from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__,
            static_url_path='',
            instance_relative_config=True)
bootstrap = Bootstrap5(app)

app.config.from_file('config.json', load=json.load)

APP_TZ = pytz.timezone(app.config['TIMEZONE'])


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
