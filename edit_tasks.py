from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class TaskForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание", validators=[DataRequired()])
    subject = StringField('Тема', validators=[DataRequired()])
    rating = StringField('Сложность (от 1 до 5)', validators=[DataRequired()])
    submit = SubmitField('Применить')
