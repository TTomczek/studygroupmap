from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, TextAreaField, DateTimeLocalField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length

from app.database import User, Studygroup


class GroupForm(FlaskForm):
    id = HiddenField('ID')
    name = StringField('Name', validators=[DataRequired('Bitte ausfüllen'), Length(min=3, max=50, message='Name muss zwischen 3 und 50 Zeichen lang sein')])
    description = TextAreaField('Beschreibung', validators=[Length(min=0, max=500, message='Beschreibung darf maximal 500 Zeichen lang sein')])
    owner = SelectField('Besitzer', validators=[DataRequired('Bitte ausfüllen')], coerce=int, choices=[])
    creation_time = DateTimeLocalField('Erstellungszeitpunkt', render_kw={"disabled": True, "readonly": True})
    is_open = BooleanField('Beitrittsanfragen erlaubt')

    def __init__(self, form=None, *, group: Studygroup = None, current_user: User = None, owner_options=None):

        super().__init__(form)

        if owner_options is not None:
            self.owner.choices = owner_options

        if group is None:
            return

        self.id.data = group.id
        self.name.data = group.name
        self.description.data = group.description
        self.creation_time.data = group.creation_time
        self.is_open.data = group.is_open

        owner_user = User.query.filter_by(id=group.owner).first()
        self.owner.data = owner_user.id

        if current_user is not None and current_user.id != group.owner:
            self.name.render_kw = {"disabled": True, "readonly": True}
            self.description.render_kw = {"disabled": True, "readonly": True}
            self.is_open.render_kw = {"disabled": True, "readonly": True}
            self.owner.render_kw = {"disabled": True, "readonly": True}
