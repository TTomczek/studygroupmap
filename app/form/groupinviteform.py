from flask_wtf import FlaskForm
from wtforms import SelectField, HiddenField, TextAreaField
from wtforms.validators import Length


class AddToGroupForm(FlaskForm):
    group = SelectField('Gruppe', validators=[], coerce=int, choices=[])
    invited_user = HiddenField('Eingeladener Benutzer')
    message = TextAreaField('Nachricht', validators=[Length(min=0, max=500, message='Nachricht darf maximal 500 Zeichen lang sein')])

    def __init__(self, form=None, *, group_choices):
        super().__init__(form)
        self.group.choices = group_choices
