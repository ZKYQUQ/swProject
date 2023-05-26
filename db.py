import traceback

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import class_mapper

db = SQLAlchemy()


def add(x):
    db.session.add(x)


def add_all(x):
    db.session.add_all(x)


def flush():
    db.session.flush()


def commit():
    try:
        db.session.commit()
    except Exception:
        traceback.print_exc()


def to_dict(model):
    if type(model) == list:
        return [to_dict(i) for i in model]
    columns = [c.key for c in class_mapper(model.__class__).columns]
    return dict((c, getattr(model, c)) for c in columns)


# User
class User(db.Model):
    __tablename__ = 'Users'
    # id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sid = db.Column(db.String(20), primary_key=True, nullable=False)
    nickname = db.Column(db.String(255), nullable=False)


# # Course
# class Course(db.Model):
#     __tablename__ = 'Courses'
#     sid = db.Column(db.String(20), primary_key=True, nullable=False)
#     filename = db.Column(db.String(100), nullable=False)
#
#
# # check entry in Courses
# def check_course(sid):
#     q = Course.query.filter_by(sid=sid).first()
#     if q:
#         return True
#     else:
#         return False
#
#
# def insert_course(sid, filename):
#     try:
#         u = Course(sid=sid, filename=filename)
#         add(u)
#         commit()
#         return True
#     except Exception:
#         return False
#
#
# def get_filename(sid):
#     q = Course.query.filter_by(sid=sid).first()
#     return q.filename


# check entry in Users
def check_user(sid):
    q = User.query.filter_by(sid=sid).first()
    if q:
        return True
    else:
        return False


def insert_user(sid, nickname):
    try:
        u = User(sid=sid, nickname=nickname)
        add(u)
        commit()
        return True
    except Exception:
        return False


def get_nickname(sid):
    q = User.query.filter_by(sid=sid).first()
    return q.nickname


def set_nickname(sid, nickname):
    q = User.query.filter_by(sid=sid).first()
    q.nickname = nickname
    add(q)
    commit()
