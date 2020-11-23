import random

import flask
from flask import Flask, render_template

import forms
from mydata import db, migrate, Goal, Teacher, Request, Booking, teachers_list
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate.init_app(app, db)
app.app_context().push()


@app.route('/')
def main_view():
    goals = db.session.query(Goal.eng_name, Goal.ru_name, Goal.pic).all()
    all_teachers = teachers_list(db.session.query(Teacher).all())
    random.shuffle(all_teachers)
    teachers_for_main = all_teachers[0:6]
    return render_template("index.html", goals=goals, teachers=teachers_for_main)


@app.route('/goals/<goal>/')
def goals_view(goal):
    desired_goal = db.session.query(Goal).filter(Goal.eng_name == goal).first_or_404()
    its_goal = desired_goal.ru_name
    item_for_goal = desired_goal.pic
    teachers_for_goal = teachers_list(desired_goal.teachers)
    return render_template("goal.html", teachers=teachers_for_goal, its_goal=its_goal, item_for_goal=item_for_goal)


@app.route('/profiles/<int:teacher_id>/')
def teachers_profile_view(teacher_id):
    day_of_the_week = {
        "mon": "Понедельник",
        "tue": "Вторник",
        "wed": "Среда",
        "thu": "Четверг",
        "fri": "Пятница",
        "sat": "Суббота",
        "sun": "Воскресенье"
    }
    desired_teacher = db.session.query(Teacher).get_or_404(teacher_id)
    teacher = teachers_list([desired_teacher])
    return render_template("profile.html", teacher=teacher[0], day_of_the_week=day_of_the_week)


@app.route('/request/', methods=["POST", "GET"])
def request_view():
    form = forms.RequestForm()
    if flask.request.method == 'GET':
        return render_template("request.html", form=form)
    if form.validate_on_submit():
        goal = form.goal.data
        goal_id = db.session.query(Goal).filter(Goal.ru_name == goal).scalar()
        time = form.time.data
        name = form.clientName.data
        phone = form.clientPhone.data
        request = Request(study_hours=time, client_phone=phone, client_name=name, goal=goal_id)
        db.session.add(request)
        db.session.commit()
        return render_template("request_done.html", form=form, goal=goal, time=time, name=name, phone=phone)
    return render_template("request.html", form=form)


@app.route('/booking/<int:teacher_id>/<day>/<time>/', methods=["POST", "GET"])
def booking_view(teacher_id, day, time):
    form = forms.BookingForm()
    desired_teacher = db.session.query(Teacher).get_or_404(teacher_id)
    teacher = teachers_list([desired_teacher])
    day_of_the_week = {
        "mon": "Понедельник",
        "tue": "Вторник",
        "wed": "Среда",
        "thu": "Четверг",
        "fri": "Пятница",
        "sat": "Суббота",
        "sun": "Воскресенье"
    }
    time = time.replace("&", ":")
    if flask.request.method == 'GET':
        return render_template("booking.html", form=form, day=day, day_of_the_week=day_of_the_week, teacher=teacher[0], time=time)
    if form.validate_on_submit():
        client_name = form.clientName.data
        client_phone = form.clientPhone.data
        client_weekday = form.clientWeekday.data
        client_time = form.clientTime.data
        booking = Booking(
            day=client_weekday,
            time=client_time,
            client_phone=client_phone,
            client_name=client_name,
            teacher=desired_teacher
        )
        db.session.add(booking)
        db.session.commit()
        return render_template("booking_done.html",
                               day=day_of_the_week[day],
                               time=client_time,
                               clientName=client_name,
                               clientPhone=client_phone
                               )
    return render_template("booking.html", form=form, day=day, day_of_the_week=day_of_the_week, teacher=teacher[0], time=time)


@app.route('/profiles/')
def all_profiles_view():
    goals = db.session.query(Goal.eng_name, Goal.ru_name, Goal.pic).all()
    all_teachers = teachers_list(db.session.query(Teacher).all())
    return render_template("all_profiles.html", goals=goals, teachers=all_teachers)


@app.errorhandler(404)
def render_not_found(error):
    return render_template('404_page.html')


if __name__ == '__main__':
    app.run()
