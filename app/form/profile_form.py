from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError

from app.database import User


class ProfileForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired('Bitte ausfüllen'), Length(min=3, max=50, message='Benutzername muss zwischen 3 und 50 Zeichen lang sein')])
    password = PasswordField('Neues Passwort', validators=[])
    password_repeat = PasswordField('Neues Passwort wiederholen', validators=[])
    firstname = StringField('Vorname', validators=[Length(min=3, max=50, message='Vorname muss zwischen 3 und 50 Zeichen lang sein')])
    lastname = StringField('Nachname', validators=[Length(min=3, max=50, message='Nachname muss zwischen 3 und 50 Zeichen lang sein')])
    email = StringField('E-Mail-Adresse', validators=[DataRequired('Bitte ausfüllen'), Email('Bitte gültige E-Mail-Adresse angeben')])
    phone = StringField('Telefonnummer', validators=[Length(min=3, max=50, message='Telefonnummer muss zwischen 3 und 50 Zeichen lang sein')])
    studentnumber = StringField('Matrikelnummer', validators=[Length(min=3, max=15, message='Matrikelnummer muss zwischen 3 und 15 Zeichen lang sein')])
    courseofstudy = StringField('Studiengang', validators=[Length(min=3, max=50, message='Studiengang muss zwischen 3 und 50 Zeichen lang sein')])
    semester = IntegerField('Semester', validators=[NumberRange(min=1, max=99, message='Semester muss zwischen 1 und 99 liegen')])
    street = StringField('Straße', validators=[Length(min=3, max=50, message='Straße muss zwischen 3 und 50 Zeichen lang sein')])
    postcode = StringField('Postleitzahl', validators=[Length(min=4, max=5, message='Postleitzahl muss zwischen 4 und 5 Zeichen lang sein')])
    city = StringField('Stadt', validators=[Length(min=3, max=50, message='Stadt muss zwischen 3 und 50 Zeichen lang sein')])
    country = StringField('Land', validators=[Length(min=3, max=50, message='Land muss zwischen 3 und 50 Zeichen lang sein')])

    def __init__(self, form=None, *, user: User = None):

        super().__init__(form)

        if user is None:
            return

        self.username.data = user.username
        self.password.data = ""
        self.password_repeat.data = ""
        self.firstname.data = user.firstname
        self.lastname.data = user.lastname
        self.email.data = user.email
        self.phone.data = user.phone
        self.studentnumber.data = user.studentnumber
        self.courseofstudy.data = user.courseofstudy
        self.semester.data = user.semester
        self.street.data = user.street
        self.postcode.data = user.postcode
        self.city.data = user.city
        self.country.data = user.country

    @staticmethod
    def validate_password(form, field):
        if field.data == "":
            return

        if 8 > len(field.data) > 72:
            raise ValidationError('Passwort muss zwischen 8 und 72 Zeichen lang sein')

    @staticmethod
    def validate_password_repeat(form, field):
        if field.data != form.password.data:
            raise ValidationError('Passwörter müssen übereinstimmen')

        if field.data == "":
            return

