from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, RadioField
from wtforms.fields.html5 import TelField
from wtforms.validators import InputRequired

from MyData import db, Goal
#
# goal_choices = []
# goals = db.session.query(Goal.ru_name).all()
# for goal in goals:
#     goal_choices.append((goal[0], goal[0]))


class BookingForm(FlaskForm):
    clientName = StringField("Вас зовут", [InputRequired(message="Имя должно быть заполнено")])
    clientPhone = TelField("Ваш телефон", [InputRequired(message="Введите ваш номер телефона")])
    clientWeekday = HiddenField()
    clientTime = HiddenField()
    clientTeacher = HiddenField()
    submit = SubmitField("Записаться на пробный урок")


class RequestForm(FlaskForm):
    goal = RadioField('Какая цель занятий?', choices=goal_choices, default="Для путешествий")
    time = RadioField('Сколько времени есть?', choices=[
        ("1-2 часа в неделю", "1-2 часа в неделю"),
        ("3-5 часов в неделю", "3-5 часов в неделю"),
        ("5-7 часов в неделю", "5-7 часов в неделю"),
        ("7-10 часов в неделю", "7-10 часов в неделю")
    ], default="1-2 часа в неделю")
    clientName = StringField("Вас зовут", [InputRequired(message="Имя должно быть заполнено")])
    clientPhone = TelField("Ваш телефон", [InputRequired(message="Введите ваш номер телефона")])
    submit = SubmitField("Найдите мне преподавателя")
