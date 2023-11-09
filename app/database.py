from datetime import datetime

import bcrypt
import pytz
from flask_login import UserMixin
from sqlalchemy import text

from app import db, app, geocode

TZ = app.config['TIMEZONE']


class User(UserMixin, db.Model):
    __name__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(72), nullable=False)
    firstname = db.Column(db.String(50), nullable=False, default="")
    lastname = db.Column(db.String(50), nullable=False, default="")
    email = db.Column(db.String(50), nullable=False, unique=True)
    phone = db.Column(db.String(50), nullable=False, default="")
    studentnumber = db.Column(db.Integer, nullable=False, default=0)
    courseofstudy = db.Column(db.String(50), nullable=False, default="")
    semester = db.Column(db.Integer, nullable=False, default=1)
    street = db.Column(db.String(50), nullable=False, default="")
    postcode = db.Column(db.String(5), nullable=False, default="")
    city = db.Column(db.String(50), nullable=False, default="")
    country = db.Column(db.String(50), nullable=False, default="")
    latitude = db.Column(db.Float, nullable=True, default=0.0)
    longitude = db.Column(db.Float, nullable=True, default=0.0)
    isFirstLogin = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self,
                 username,
                 email,
                 password,
                 id=None,
                 studentnumber=0):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.studentnumber = studentnumber

    def __str__(self):
        return self.id + "-" + self.username + "-" + self.email

    def __eq__(self, other):
        return self.id == other.id

    def update_location(self):
        location = geocode(self.street + ", " + self.postcode + " " + self.city + ", " + self.country)
        if location is not None:
            self.latitude = location.latitude
            self.longitude = location.longitude
            db.session.commit()

    @staticmethod
    def hash_password(password):

        salt = bcrypt.gensalt()
        pepper = app.config['PEPPER']

        password_bytes = password.encode('utf-8')
        pepper_bytes = pepper.encode('utf-8')

        hash_with_pepper = bcrypt.hashpw(password_bytes, pepper_bytes)
        hash_with_salt = bcrypt.hashpw(hash_with_pepper, salt)
        return hash_with_salt.decode('utf-8')

    @staticmethod
    def check_password(password, hashed_password):

        pepper = app.config['PEPPER']

        password_bytes = password.encode('utf-8')
        pepper_bytes = pepper.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')

        hash_with_pepper = bcrypt.hashpw(password_bytes, pepper_bytes)
        return bcrypt.checkpw(hash_with_pepper, hashed_password_bytes)


class Studygroup(db.Model):
    __name__ = 'studygroups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    creator = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creation_time = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone(TZ)))

    def __init__(self, id=None, name="", description="", creator=0):
        self.id = id
        self.name = name
        self.description = description
        self.creator = creator


class StudygroupUser(db.Model):
    __name__ = 'studygroupusers'

    id = db.Column(db.Integer, primary_key=True)
    studygroup = db.Column(db.Integer, db.ForeignKey('studygroup.id'), nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joiningdate = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone(TZ)))

    def __init__(self, studygroup, user, id=None, joiningdate=datetime.now(pytz.timezone(TZ))):
        self.id = id
        self.studygroup = studygroup
        self.user = user
        self.joiningdate = joiningdate


def get_studygroups_of_user_for_dashboard(user):
    studygroups = db.session.execute(
        text("SELECT sg.*, count(sgu.user) as member_count FROM Studygroup sg "
             "INNER JOIN studygroup_user sgu ON sg.id = sgu.studygroup "
             "WHERE sg.id IN (SELECT DISTINCT sgu1.studygroup FROM studygroup_user sgu1 WHERE sgu1.user = :user)"
             "GROUP BY sg.id;"), {"user": user.id}).fetchall()
    return studygroups
