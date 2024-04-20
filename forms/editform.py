from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class EditForm(FlaskForm):

    name = StringField('Имя пользователя', validators=[DataRequired()])
    channels = StringField("Ваши каналы (через пробел)", validators=[DataRequired()])
    submit = SubmitField('Подтвердить')
