from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class SolveForm(FlaskForm):
    content = TextAreaField("Решение", validators=[DataRequired()])
    submit = SubmitField('Отправить')
