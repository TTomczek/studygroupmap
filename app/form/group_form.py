from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, TextAreaField, DateTimeLocalField
from wtforms.validators import DataRequired, Length

from app.database import User, Studygroup


class GroupForm(FlaskForm):
    id = HiddenField('ID')
    name = StringField('Name', validators=[DataRequired('Bitte ausfüllen'), Length(min=3, max=50, message='Name muss zwischen 3 und 50 Zeichen lang sein')])
    description = TextAreaField('Beschreibung', validators=[Length(min=0, max=500, message='Beschreibung darf maximal 500 Zeichen lang sein')])
    owner = StringField('Besitzer', render_kw={"disabled": True, "readonly": True})
    creation_time = DateTimeLocalField('Erstellungszeitpunkt', render_kw={"disabled": True, "readonly": True})

    def __init__(self, form=None, *, group: Studygroup = None, current_user: User = None):

        super().__init__(form)

        if group is None:
            return

        self.id.data = group.id
        self.name.data = group.name
        self.description.data = group.description
        self.creation_time.data = group.creation_time

        owner_user = User.query.filter_by(id=group.owner).first()
        self.owner.id = owner_user.id
        self.owner.data = owner_user.firstname + " " + owner_user.lastname + " (" + owner_user.username + ")"

        if current_user is not None and current_user.id != group.owner:
            self.name.render_kw = {"disabled": True, "readonly": True}
            self.description.render_kw = {"disabled": True, "readonly": True}
