import json

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


def add_initial_user(db):

    if User.query.filter_by(email="admin@bla.outer").first() is None:
        user1 = User(username="admin", email="admin@bla.outer", password=User.hash_password("admin"))
        user1.firstname = "Admin"
        user1.lastname = "of Network"
        user1.city = "Berlin"
        user1.country = "Germany"
        user1.street = "Straße des 17. Juni 135"
        user1.postcode = "10623"
        user1.phone = "+49 30 314-0"
        user1.studentnumber = "1234567890"
        user1.courseofstudy = "Computer Science"
        user1.semester = "3"

        db.session.add(user1)
        db.session.commit()


db = SQLAlchemy()
app = Flask(__name__,
            static_folder='../static',
            template_folder='../templates',
            static_url_path='')

app.config.from_file('config.json', load=json.load)


with app.app_context():
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .models import User, Studygroup, StudygroupUser
    db.create_all()
    db.session.commit()

    add_initial_user(db)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
