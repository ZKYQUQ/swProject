import db
import execJs
import user
import webvpn


# get course in week format
def get_course(username, term, week):
    # the specified schedule with given username and week doesn't exist
    if not db.term_courses_exist(username, term):
        if not db.check_user(username):
            return False, "No such user when attempting to get course!"
        sid, pwd = db.get_sid_pwd(username)

        # login first
        if not (sid and pwd):
            return False, "Course sid and pwd needed!"
        init_response = user.init(sid)
        # get parameters
        cookie = init_response['cookie']
        execution = init_response['execution']
        captcha = init_response['captcha']
        salt = init_response['salt']
        # calculate password
        encrypted_pwd = execJs.exec_encryptpassword(pwd, salt)
        verify_response = user.verify(sid, encrypted_pwd, execution, cookie, captcha)
        if verify_response == False:
            return False, "Login course website failed!"

        # get course
        get_result = webvpn.get_course(username, cookie, term)
        if get_result == False:
            return False, "Get course from website fail!"

    if not db.term_courses_exist(username, term):
        return False, "No courses of this user!"
    # query specified courses
    result, filtered_courses = db.get_courses(username, term, week)
    if not result:
        return False, "Query week num is incorrect!"
    # sort original json objects by WEEKDAY and STARTSEQ
    sorted_courses = sorted(filtered_courses, key=lambda x: (x['weekDay'], x['startSeq']))
    # fill week courses
    week_course = []
    for day in range(1, 8):
        day_course = []
        for course in sorted_courses:
            if int(course['weekDay']) == day:
                start_seq = int(course['startSeq'])
                end_seq = int(course['endSeq'])
                for i in range(start_seq, end_seq + 1):
                    tmp_course = course.copy()
                    tmp_course.pop('weekDay')
                    tmp_course.pop('startSeq')
                    tmp_course.pop('endSeq')
                    tmp_course['courseIndex'] = str(i)
                    day_course.append(tmp_course)
        if len(day_course) == 0:
            continue
        week_course.append({'day': day, 'courses': day_course})
    return True, {"weekCourses": week_course}


# get schedule
def get_schedule(username):
    # the specified schedule with given username doesn't exist
    if not db.schedule_exist(username):
        if not db.check_user(username):
            return False, "No such user when attempting to get schedule!"
        # get schedule
        get_result = webvpn.get_schedule(username)
        if not get_result:
            return False, "Get schedule from website fail!"

    if not db.schedule_exist(username):
        return False, "No schedule of this user!"
    # query specified schedules
    events = db.get_schedules(username)
    return True, events


# update schedule
def update_schedule(username, event):
    if not db.check_user(username):
        return False
    if db.update_schedule(username, event):
        return True
    return False


# create schedule
def insert_schedule(username, event):
    if not db.check_user(username):
        return False
    db.insert_schedule(username, event)
    return True


# mark schedule
def mark_schedule(username, eventID):
    if not db.check_user(username):
        return False
    if db.mark_schedule(username, eventID):
        return True
    return False
