from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, TextAreaField, DateTimeLocalField
from wtforms.validators import DataRequired, Length

from app.database import User


class GroupForm(FlaskForm):
    id = HiddenField('ID')
    name = StringField('Name', validators=[DataRequired('Bitte ausfüllen'), Length(min=3, max=50, message='Name muss zwischen 3 und 50 Zeichen lang sein')])
    description = TextAreaField('Beschreibung', validators=[Length(min=0, max=500, message='Beschreibung darf maximal 500 Zeichen lang sein')])
    creator = StringField('Ersteller', render_kw={"disabled": True, "readonly": True})
    creation_time = DateTimeLocalField('Erstellungszeitpunkt', render_kw={"disabled": True, "readonly": True})

    def __init__(self, form=None, *, group=None):

        super().__init__(form)

        if group is None:
            return

        self.id.data = group.id
        self.name.data = group.name
        self.description.data = group.description
        self.creation_time.data = group.creation_time

        creator_user = User.query.filter_by(id=group.creator).first()
        self.creator.id = creator_user.id
        self.creator.data = creator_user.firstname + " " + creator_user.lastname + " (" + creator_user.username + ")"
