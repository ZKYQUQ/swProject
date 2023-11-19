import traceback

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
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


class User(db.Model):
    __tablename__ = 'User'
    # id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), primary_key=True, nullable=False)
    password = db.Column(db.String(20))
    sid = db.Column(db.String(20))
    spwd = db.Column(db.String(20))
    nickname = db.Column(db.String(255))


# user register
def user_register(username, password):
    if check_user(username) == False:
        if (insert_user(username, password)):
            return True
    return False


# user login
def user_login(username, password):
    user = User.query.filter_by(username=username).first()
    if user:
        if user.password == password:
            return True
    return False


# user update
def user_update(username, password, sid, spwd, nickname):
    user = User.query.filter_by(username=username).first()
    if user:
        user.sid = sid if sid else user.sid
        user.spwd = spwd if spwd else user.spwd
        user.nickname = nickname if nickname else user.nickname
        commit()
        return True
    return False


# check entry in User
def check_user(username):
    q = User.query.filter_by(username=username).first()
    if q:
        return True
    else:
        return False


def insert_user(username, password):
    try:
        u = User(username=username, password=password)
        add(u)
        commit()
        return True
    except Exception:
        return False


def get_sid_pwd(username):
    q = User.query.filter_by(username=username).first()
    return q.sid, q.spwd


# Course
class Course(db.Model):
    __tablename__ = 'Course'
    username = db.Column(db.String(40), primary_key=True, nullable=False)
    term = db.Column(db.String(20), primary_key=True, nullable=False)
    courseName = db.Column(db.String(40), primary_key=True, nullable=False)
    courseNo = db.Column(db.String(40), nullable=False)
    teacherName = db.Column(db.String(20), nullable=False)
    classNo = db.Column(db.String(256))
    roomNo = db.Column(db.String(40), nullable=False)
    startTime = db.Column(db.String(20), nullable=False)
    endTime = db.Column(db.String(20), nullable=False)
    startWeek = db.Column(db.Integer, nullable=False)
    endWeek = db.Column(db.Integer, nullable=False)
    detail = db.Column(db.String(256), nullable=False)
    weekInfo = db.Column(db.String(40), nullable=False)
    weekDay = db.Column(db.Integer, primary_key=True, nullable=False)
    startSeq = db.Column(db.Integer, nullable=False)
    endSeq = db.Column(db.Integer, nullable=False)
    firstDay = db.Column(db.String(20), nullable=False)


def insert_courses(username, term, courses, first_day):
    # print("insert_courses")
    course_list = []
    for course in courses:
        newCourse = Course(username=username, term=term, courseName=course["COURSENAME"], courseNo=course["COURSENO"],
                           teacherName=course["TEACHERNAME"], classNo=course["CLASSNO"]
                           , roomNo=course["ROOMNO"], startTime=course["STARTTIME"], endTime=course["ENDTIME"],
                           startWeek=course["STARTWEEK"], endWeek=course["ENDWEEK"]
                           , detail=course["DETAIL"], weekInfo=course["WEEKINFO"], weekDay=course["WEEKDAY"],
                           startSeq=course["STARTSEQ"], endSeq=course["ENDSEQ"], firstDay=first_day)
        course_list.append(newCourse)
        # print("course added")
    add_all(course_list)
    commit()


def term_courses_exist(username, term):
    if Course.query.filter(and_(Course.username == username, Course.term == term)).first():
        return True
    return False


def get_courses(username, term, week):
    week = int(week)
    testInfo = Course.query.filter(and_(Course.username == username, Course.term == term)).first().weekInfo
    if week > len(testInfo) or week <= 0:
        return False, None
    courses = Course.query.filter(and_(Course.username == username, Course.term == term)).all()
    filtered_courses = []
    for course in courses:
        weekInfo = course.weekInfo
        if weekInfo[week - 1] == '1':
            dict = {}
            dict["courseName"] = course.courseName
            dict["courseNo"] = course.courseNo
            dict["teacherName"] = course.teacherName
            dict["classNo"] = course.classNo
            dict["roomNo"] = course.roomNo
            dict["startTime"] = course.startTime
            dict["endTime"] = course.endTime
            dict["startWeek"] = course.startWeek
            dict["endWeek"] = course.endWeek
            dict["weekDay"] = course.weekDay
            dict["startSeq"] = course.startSeq
            dict["endSeq"] = course.endSeq
            filtered_courses.append(dict)
    return True, filtered_courses


def get_all_courses(username):
    courses = Course.query.filter_by(username=username).all()
    courses_list=[]
    for course in courses:
        dict = {}
        dict["courseName"] = course.courseName
        dict["startTime"] = course.startTime
        dict["weekDay"] = course.weekDay
        dict["weekInfo"] = course.weekInfo
        dict["detail"] = course.detail
        dict["firstDay"] = course.firstDay
        courses_list.append(dict)
    return True, courses_list


# Schedule
class Schedule(db.Model):
    __tablename__ = 'Schedule'
    username = db.Column(db.String(40), primary_key=True, nullable=False)
    eventID = db.Column(db.Integer, primary_key=True, nullable=False)
    date = db.Column(db.String(40))
    time = db.Column(db.String(40))
    name = db.Column(db.String(128))
    description = db.Column(db.String(4096))
    isFinished = db.Column(db.Boolean)


# insert schedules
def insert_schedules(schedules):
    list = []
    for schedule in schedules:
        element = Schedule(username=schedule["username"], eventID=schedule["eventID"],
                           date=schedule["date"], time=schedule["time"],
                           name=schedule["name"], description=schedule["description"],
                           isFinished=schedule["isFinished"])
        list.append(element)
    add_all(list)
    commit()


# insert single schedule
def insert_schedule(username, schedule):
    schedules = Schedule.query.filter_by(username=username).all()
    schedule_num = len(schedules)
    element = Schedule(username=username, eventID=schedule_num,
                       date=schedule["date"], time=schedule["time"],
                       name=schedule["name"], description=schedule["description"],
                       isFinished=schedule["isFinished"])
    add(element)
    commit()


# update schedule
def update_schedule(username, input):
    schedule = Schedule.query.filter(
        and_(Schedule.username == username, Schedule.eventID == input["eventID"])).first()
    if schedule:
        schedule.date = input["date"]
        schedule.time = input["time"]
        schedule.name = input["name"]
        schedule.description = input["description"]
        schedule.isFinished = input["isFinished"]
        commit()
        return True
    return False


# mark finished
def mark_schedule(username, eventID):
    schedule = Schedule.query.filter(
        and_(Schedule.username == username, Schedule.eventID == eventID)).first()
    if schedule:
        schedule.isFinished = True
        commit()
        return True
    return False


# get schedules
def get_schedules(username):
    schedules = Schedule.query.filter_by(username=username).all()
    events = []
    for schedule in schedules:
        dict = {}
        dict["eventID"] = schedule.eventID
        dict["date"] = schedule.date
        dict["time"] = schedule.time
        dict["name"] = schedule.name
        dict["description"] = schedule.description
        dict["isFinished"] = schedule.isFinished
        events.append(dict)
    return {"events": events}


# check if schedule of someone exists
def schedule_exist(username):
    if Schedule.query.filter_by(username=username).first():
        return True
    return False
