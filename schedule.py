import json
import os.path

import config
import webvpn
import icalendar
import datetime
import uuid
import saver

# import db

time_table = [
    [[8, 0], [8, 45]],
    [[8, 50], [9, 35]],
    [[9, 55], [10, 40]],
    [[10, 45], [11, 30]],
    [[11, 35], [12, 20]],
    [[13, 20], [14, 5]],
    [[14, 10], [14, 55]],
    [[15, 15], [16, 0]],
    [[16, 5], [16, 50]],
    [[16, 55], [17, 40]],
    [[18, 30], [19, 15]],
    [[19, 20], [20, 5]],
    [[20, 10], [20, 55]],
]


# lec_sequence represents the start/end serial number of lecture,lec_seq_type indicates whether start/end
def get_time(first_day, week, weekday, lec_sequence, lec_seq_type):
    # datetime takes things like days in month,time zone and so on into account
    delta = datetime.timedelta(weeks=week - 1, days=weekday - 1, hours=time_table[lec_sequence - 1][lec_seq_type][0],
                               minutes=time_table[lec_sequence - 1][lec_seq_type][1])
    return first_day + delta


# save schedule and return url dict
def get_ics_url(cookie, sid, term):
    # ics file exists
    # filename = sid + "schedule.ics"
    filename = sid + term + "schedule.ics"
    filepath = os.path.join(config.ics_save_path, filename)
    if os.path.exists(filepath):
        print("Same schedule exists!")
        return {'url': config.ics_url_prefix + filename}
    # get and schedule in json
    dic = webvpn.get_schedule_term(sid, cookie, term)
    # fill calendar
    cal = icalendar.Calendar()
    cal['VERSION'] = '2.0'  # version
    cal['X-WR-CALNAME'] = '个人课程表'  # calendar name
    cal['TZID'] = 'Asia/Shanghai'  # time zone
    first_day = datetime.datetime.strptime(dic['first_day'], r'%Y-%m-%d')
    for lecture in dic['data']:
        week_length = len(lecture['SKZC'])
        for week in range(week_length):
            # lectures exist in this week
            if int(lecture['SKZC'][week]):
                event = icalendar.Event()  # event component
                event['UID'] = uuid.uuid4()  # unique identifier
                event['SUMMARY'] = lecture['KCM']  # summary aka title
                event['LOCATION'] = lecture['JASMC']  # location
                # start&end time
                event.add('DTSTART', get_time(first_day, week + 1, lecture['SKXQ'], lecture['KSJC'], 0))
                event.add('DTEND', get_time(first_day, week + 1, lecture['SKXQ'], lecture['JSJC'], 1))
                event['DESCRIPTION'] = "节数:" + str(lecture['KSJC']) + "-" + str(lecture['JSJC']) + "\n" + \
                                       "课程号:" + str(lecture["KCH"]) + "\n" + \
                                       "教师:" + str(lecture['SKJS']) + "\n" + \
                                       "班级号:" + str(lecture['SKBJ']) + "\n" + \
                                       "详细信息:" + str(lecture['YPSJDD'])
                cal.add_component(event)
    # filename = saver.save_ics(sid + 'schedule.ics', cal.to_ical())
    filename = saver.save_ics(sid + term + 'schedule.ics', cal.to_ical())
    # insert entry into courses
    # db.insert_course(sid, filename)
    return {'url': config.ics_url_prefix + filename}


# get schedule of specified week and return week schedule dict
def get_week_schedule(sid, target_week, term):
    target_week = int(target_week)
    filename = sid + term + "schedule.json"
    filepath = os.path.join(config.json_save_path, filename)
    if not os.path.exists(filepath):
        return {'data': 'please get your schedule first'}
    # make response data in specified format
    with open(filepath, 'r') as f:
        data = json.load(f)
    # add valid courses
    filtered_courses = []
    for course in data['courses']:
        week = course['WEEKINFO']
        if week[target_week - 1] == '1':
            filtered_courses.append(course)
    # sort original json objects by WEEKDAY and STARTSEQ
    sorted_courses = sorted(filtered_courses, key=lambda x: (x['WEEKDAY'], x['STARTSEQ']))
    # fill week courses
    week_course = []
    for day in range(1, 8):
        day_course = []
        for course in sorted_courses:
            if int(course['WEEKDAY']) == day:
                start_seq = int(course['STARTSEQ'])
                end_seq = int(course['ENDSEQ'])
                for i in range(start_seq, end_seq + 1):
                    tmp_course = course.copy()
                    tmp_course['COURSEINDEX'] = str(i)
                    day_course.append(tmp_course)
        if len(day_course) == 0:
            continue
        week_course.append({'day': day, 'courses': day_course})
    return {'data': week_course}
