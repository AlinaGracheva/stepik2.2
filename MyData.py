import json
from datetime import datetime

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql.json import JSONB

from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app


app = create_app()
app.app_context().push()

teachers_goals_association = db.Table(
    "teachers_goals",
    db.Column("teacher_id", db.Integer, db.ForeignKey("teachers.id")),
    db.Column("goal_id", db.Integer, db.ForeignKey("goals.id"))
)


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    about = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String(), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    booking = db.relationship("Booking", back_populates="teacher")
    goals = db.relationship(
        "Goal", secondary=teachers_goals_association, back_populates="teachers"
    )
    free = db.Column(JSONB, nullable=False)


class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer(), primary_key=True)
    eng_name = db.Column(db.String(), nullable=False)
    ru_name = db.Column(db.String(), nullable=False)
    pic = db.Column(db.String(), nullable=False)
    teachers = db.relationship(
        "Teacher", secondary=teachers_goals_association, back_populates="goals"
    )
    requests = db.relationship("Request", back_populates="goal")


class Booking(db.Model):
    __tablename__ = 'booking_table'
    id = db.Column(db.Integer(), primary_key=True)
    day = db.Column(db.String(), nullable=False)
    time = db.Column(db.String(), nullable=False)
    client_phone = db.Column(db.String(), nullable=False)
    client_name = db.Column(db.String(), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.now)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    teacher = db.relationship("Teacher", back_populates="booking")


class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer(), primary_key=True)
    study_hours = db.Column(db.String(), nullable=False)
    client_phone = db.Column(db.String(), nullable=False)
    client_name = db.Column(db.String(), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey("goals.id"))
    goal = db.relationship("Goal", back_populates="requests")


def data_import(data_dict):
    for key, val in data_dict.get('goals').items():
        to_insert = Goal(
            eng_name=key,
            ru_name=val,
            pic=data_dict.get('goals_items')[val]
        )
        db.session.add(to_insert)
        db.session.flush()
    for teacher in data_dict.get('teachers'):
        to_insert = Teacher(
            name=teacher['name'],
            about=teacher['about'],
            rating=teacher['rating'],
            picture=teacher['picture'],
            price=teacher['price'],
            free=teacher['free']
        )
        db.session.add(to_insert)
        for teachers_goal in teacher["goals"]:
            goal = Goal.query.filter(Goal.eng_name == teachers_goal).first()
            to_insert.goals.append(goal)
    db.session.commit()
    return


def teachers_list(query):
    teachers = []
    for teacher in query:
        item = {
            'id': teacher.id,
            'name': teacher.name,
            'about': teacher.about,
            'rating': teacher.rating,
            'picture': teacher.picture,
            'price': teacher.price,
            'free': teacher.free,
            'goals': []
        }
        for goal in teacher.goals:
            item['goals'].append(goal.eng_name)
        teachers.append(item)
    return teachers


if __name__ == '__main__':
    with open("data.json", encoding="utf-8") as file:
        data_from_file = json.load(file)
    data_import(data_from_file)
