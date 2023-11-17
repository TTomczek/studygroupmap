from datetime import datetime

import bcrypt
import pytz
from flask_login import UserMixin
from sqlalchemy import text, and_

from app import db, app, geocode, APP_TZ


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
        location = geocode(self.street + ", " + self.postcode + " " + self.city + ", " + self.country)
        if location is not None:
            self.latitude = location.latitude
            self.longitude = location.longitude
            db.session.commit()

    @staticmethod
    def get_studygroups_of_user_for_dashboard(user):
        studygroups = db.session.execute(
            text("SELECT sg.*, count(sgu.user) as member_count FROM Studygroup sg "
                 "INNER JOIN studygroup_user sgu ON sg.id = sgu.studygroup "
                 "WHERE sg.id IN (SELECT DISTINCT sgu1.studygroup FROM studygroup_user sgu1 WHERE sgu1.user = :user)"
                 "GROUP BY sg.id;"), {"user": user.id}).fetchall()
        return studygroups

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
        users_in_group = db.session.execute(
            text('SELECT * FROM User INNER JOIN studygroup_user ON User.id = studygroup_user.user '
                 'WHERE studygroup_user.studygroup = :studygroup'), {"studygroup": self.id}).fetchall()

        center_lat = 0
        center_lon = 0

        for user in users_in_group:
            center_lat += user.latitude
            center_lon += user.longitude

        center_lat /= len(users_in_group)
        center_lon /= len(users_in_group)

        return [center_lat, center_lon]

    def get_member(self):
        return db.session.execute(
            text('SELECT sgu.joiningdate, u.* FROM studygroup_user sgu INNER JOIN User u ON sgu.user = u.id '
                 'WHERE sgu.studygroup = :group_id'),
            {"group_id": self.id}
        ).fetchall()


class StudygroupUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studygroup = db.Column(db.Integer, db.ForeignKey('studygroup.id'), nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joiningdate = db.Column(db.DateTime, nullable=False, default=datetime.now(APP_TZ))

    def __init__(self, studygroup, user, id=None, joiningdate=datetime.now(APP_TZ)):
        self.id = id
        self.studygroup = studygroup
        self.user = user
        self.joiningdate = joiningdate

    @staticmethod
    def get_groups_ids_of_useer(user_id):
        return StudygroupUser.query.distinct(StudygroupUser.studygroup).filter_by(user=user_id).all()


class JoinRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    studygroup = db.Column(db.Integer, db.ForeignKey('studygroup.id'), nullable=False)
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


class MessageType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, default="")
    description = db.Column(db.String(500), nullable=False, default="")

    def __init__(self, name: str, description: str, id=None):
        self.id = id
        self.name = name
        self.description = description


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receiver = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(50), nullable=False, default="")
    message = db.Column(db.String(500), nullable=False, default="")
    messagedate = db.Column(db.DateTime, nullable=False, default=datetime.now(APP_TZ))
    message_type = db.Column(db.Integer, db.ForeignKey('message_type.id'), nullable=False)
    read = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, receiver: int, sender: int, title: str, message: str = "", message_type: str = "message",
                 read: bool = False, id=None, message_date=datetime.now(APP_TZ)):
        self.id = id
        self.sender = sender
        self.receiver = receiver
        self.title = title
        self.message = message
        self.messagedate = message_date
        self.read = read

        message_type_found = MessageType.query.filter_by(name=message_type).first()
        if message_type_found is None:
            print("Error: Message type not found.", message_type)
            return

        self.message_type = message_type_found.id

    @staticmethod
    def get_messages(user_id: int, unread_only: bool = False, message_type: str = "message"):

        message_type_found = MessageType.query.filter_by(name=message_type).first()

        if message_type_found is None:
            print("Error: Message type not found.", message_type)
            return []

        return Message.query.filter_by(receiver=user_id, read=unread_only, message_type=message_type_found.id).all()

    @staticmethod
    def get_message_count_for_user(user_id: int, unread_only: bool = False):

        message_type_found = MessageType.query.filter_by(name='message').first()

        if message_type_found is None:
            return 0

        return Message.query.filter_by(receiver=user_id, read=unread_only, message_type=message_type_found.id).count()

    @staticmethod
    def send_message(receiver: int, sender: int, title: str, message: str = "", message_type: str = "message"):

        message = Message(receiver, sender, title, message, message_type)
        db.session.add(message)
        db.session.commit()


class JoinRequestPresentation:
    request: JoinRequest
    invited_user: User
    invited_by: User
    group: Studygroup
    invited: bool = False

    def __init__(self, request: JoinRequest):
        self.request = request
        self.invited_user = User.query.filter_by(id=request.invited_user).first()
        self.group = Studygroup.query.filter_by(id=request.studygroup).first()

        if self.request.invited_by is not None:
            self.invited = True
            self.invited_by = User.query.filter_by(id=request.invited_by).first()


def get_join_requests_for_group(group_id: int):

    # Normalerweise werden Vergleiche mit None mit einem is gemacht, aber das funktioniert bei SqlAlchemy nicht.
    raw_join_requests = JoinRequest.query.filter(JoinRequest.accepted == None, JoinRequest.studygroup == group_id).all()

    join_requests = []
    for raw_join_request in raw_join_requests:
        join_requests.append(JoinRequestPresentation(raw_join_request))

    return join_requests


def get_invitations_for_user(user_id: int):

    # Normalerweise werden Vergleiche mit None mit einem is gemacht, aber das funktioniert bei SqlAlchemy nicht.
    raw_join_requests = JoinRequest.query.filter(JoinRequest.accepted == None, JoinRequest.invited_user == user_id).all()

    join_requests = []
    for raw_join_request in raw_join_requests:
        join_requests.append(JoinRequestPresentation(raw_join_request))

    return join_requests
