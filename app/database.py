from datetime import datetime

import bcrypt
from flask_login import UserMixin
from sqlalchemy import text

from app import db, app, APP_TZ
from app.geocoding import get_coordinates


class User(UserMixin, db.Model):
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
    can_be_invited = db.Column(db.Boolean, nullable=False, default=True)
    about_me = db.Column(db.String(1500), nullable=False, default="")

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
        return str(self.id) + "-" + self.username + "-" + self.email

    def __eq__(self, other):
        return self.id == other.id

    def update_location(self):
        """Aktualisieren der Koordinaten anhand der Adresse."""
        city_postcode = ' '.join([self.postcode, self.city])
        location_string = ','.join([self.street, city_postcode, self.country])

        latitude, longitude = get_coordinates(location_string)

        if latitude is not None and longitude is not None:

            self.latitude = latitude
            self.longitude = longitude
            db.session.commit()
        else:

            app.logger.warning("Cannot update location")

    @staticmethod
    def get_studygroups_of_user_for_dashboard(user):
        """Gibt alle Gruppen zurück, in denen der Benutzer Mitglied ist und wie viele Mitglieder diese haben."""
        return db.session.execute(
            text("SELECT sg.*, count(sgu.user) as member_count FROM Study_group sg "
                 "INNER JOIN studygroup_user sgu ON sg.id = sgu.studygroup "
                 "WHERE sg.id IN (SELECT DISTINCT sgu1.studygroup FROM studygroup_user sgu1 WHERE sgu1.user = :user)"
                 "GROUP BY sg.id;"), {"user": user.id}).fetchall()

    @staticmethod
    def hash_password(password):
        """Hashen des Passworts mit Salt und Pepper."""
        salt = bcrypt.gensalt()
        pepper = app.config['PEPPER']

        password_bytes = password.encode('utf-8')
        pepper_bytes = pepper.encode('utf-8')

        hash_with_pepper = bcrypt.hashpw(password_bytes, pepper_bytes)
        hash_with_salt = bcrypt.hashpw(hash_with_pepper, salt)
        return hash_with_salt.decode('utf-8')

    @staticmethod
    def check_password(password, hashed_password):
        """Prüfen, ob das Passwort korrekt ist."""
        pepper = app.config['PEPPER']

        password_bytes = password.encode('utf-8')
        pepper_bytes = pepper.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')

        hash_with_pepper = bcrypt.hashpw(password_bytes, pepper_bytes)
        return bcrypt.checkpw(hash_with_pepper, hashed_password_bytes)


class StudyGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creation_time = db.Column(db.DateTime, nullable=False, default=datetime.now(APP_TZ))
    is_open = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self, id=None, name="", description="", owner=0):
        self.id = id
        self.name = name
        self.description = description
        self.owner = owner

    def get_group_location(self):
        """Gibt die Koordinaten des Gruppenmittelpunkts zurück.
        Der Mittelpunkt wird aus den Koordinaten der Mitglieder berechnet."""
        users_in_group = db.session.execute(
            text('SELECT * FROM User INNER JOIN studygroup_user ON User.id = studygroup_user.user '
                 'WHERE studygroup_user.studygroup = :studygroup'), {"studygroup": self.id}).fetchall()

        center_lat = 0
        center_lon = 0

        for user in users_in_group:
            center_lat += user.latitude
            center_lon += user.longitude

        user_count = len(users_in_group) if len(users_in_group) > 0 else 1
        center_lat /= user_count
        center_lon /= user_count

        return [center_lat, center_lon]

    def get_member(self):
        """Gibt alle Mitglieder der Gruppe zurück."""
        return db.session.execute(
            text('SELECT sgu.joiningdate, u.* FROM studygroup_user sgu INNER JOIN User u ON sgu.user = u.id '
                 'WHERE sgu.studygroup = :group_id'),
            {"group_id": self.id}
        ).fetchall()

    def get_member_count(self):
        """Gibt die Anzahl der Mitglieder der Gruppe zurück."""
        return StudygroupUser.query.filter_by(studygroup=self.id).count()

    def get_owner_user(self):
        """Gibt den Besitzer der Gruppe, als User, zurück."""
        return User.query.filter_by(id=self.owner).first()


class StudygroupUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studygroup = db.Column(db.Integer, db.ForeignKey('study_group.id'), nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joiningdate = db.Column(db.DateTime, nullable=False, default=datetime.now(APP_TZ))

    def __init__(self, studygroup, user, id=None, joiningdate=datetime.now(APP_TZ)):
        self.id = id
        self.studygroup = studygroup
        self.user = user
        self.joiningdate = joiningdate

    @staticmethod
    def get_groups_ids_of_user(user_id):
        """Gibt die IDs aller Gruppen zurück, in denen der Benutzer Mitglied ist."""
        return StudygroupUser.query.distinct(StudygroupUser.studygroup).filter_by(user=user_id).all()


class JoinRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studygroup = db.Column(db.Integer, db.ForeignKey('study_group.id'), nullable=False)
    invited_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    invited_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    requestdate = db.Column(db.DateTime, nullable=False, default=datetime.now(APP_TZ))
    message = db.Column(db.String(500), nullable=False, default="")
    accepted = db.Column(db.Boolean, nullable=True, default=None)

    def __init__(self, studygroup_id: int, invited_user_id: int, invited_by_id: int = None, id=None, message="",
                 request_date=datetime.now(APP_TZ)):
        self.id = id
        self.studygroup = studygroup_id
        self.invited_user = invited_user_id
        self.invited_by = invited_by_id
        self.message = message
        self.requestdate = request_date


class JoinRequestPresentation:
    request: JoinRequest
    invited_user: User
    invited_by: User = None
    group: StudyGroup
    invited: bool = False

    def __init__(self, request: JoinRequest):
        self.request = request
        self.invited_user = User.query.filter_by(id=request.invited_user).first()
        self.group = StudyGroup.query.filter_by(id=request.studygroup).first()

        if self.request.invited_by is not None:
            self.invited = True
            self.invited_by = User.query.filter_by(id=request.invited_by).first()


def get_join_requests_for_group(group_id: int):
    """Gibt alle Beitrittsanfragen für eine Gruppe zurück."""
    # Normalerweise werden Vergleiche mit None mit einem is gemacht, aber das funktioniert bei SqlAlchemy nicht.
    raw_join_requests = JoinRequest.query.filter(JoinRequest.accepted == None, JoinRequest.studygroup == group_id).all()

    join_requests = []
    for raw_join_request in raw_join_requests:
        join_requests.append(JoinRequestPresentation(raw_join_request))

    return join_requests


def get_invitations_for_user(user_id: int):
    """Gibt alle Einladungen für einen Benutzer zurück."""
    # Normalerweise werden Vergleiche mit None mit einem is gemacht, aber das funktioniert bei SqlAlchemy nicht.
    raw_join_requests = JoinRequest.query.filter(JoinRequest.accepted == None, JoinRequest.invited_user == user_id,
                                                 JoinRequest.invited_by != None).all()

    join_requests = []
    for raw_join_request in raw_join_requests:
        join_requests.append(JoinRequestPresentation(raw_join_request))

    return join_requests
