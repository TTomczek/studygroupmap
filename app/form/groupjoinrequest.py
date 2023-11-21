from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField
from wtforms.validators import Length


class GroupJoinRequest(FlaskForm):
    group_id = HiddenField('Gruppen-ID', validators=[])
    message = TextAreaField('Nachricht', validators=[Length(min=0, max=500, message='Nachricht darf maximal 500 Zeichen lang sein')])
    submit = SubmitField('Anfrage senden')

    def __init__(self, form=None, *, group_id):
        super().__init__(form)
        self.group_id.data = group_id
