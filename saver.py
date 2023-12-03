import datetime
import json
import os
import traceback

import icalendar

import config
import db

time_table1 = [
    ["08:00", "08:45"],
    ["08:50", "09:35"],
    ["09:55", "10:40"],
    ["10:45", "11:30"],
    ["11:35", "12:20"],
    ["13:20", "14:05"],
    ["14:10", "14:55"],
    ["15:15", "16:00"],
    ["16:05", "16:50"],
    ["16:55", "17:40"],
    ["18:30", "19:15"],
    ["19:20", "20;05"],
    ["20:10", "20:55"],
]


# save schedule in json type
def save_json(sid, term, content):
    try:
        new_data = []
        for course in content['data']:
            weeks = course['SKZC']
            start_week = weeks.find('1') + 1
            end_week = weeks.rfind('1') + 1
            new_course = {
                'COURSENAME': course['KCM'],  # name
                'COURSENO': course['KCH'],  # number
                'TEACHERNAME': course['SKJS'],  # teacher
                'CLASSNO': course['SKBJ'],  # class_number
                'ROOMNO': course['JASMC'],  # location
                'STARTTIME': time_table1[int(course['KSJC']) - 1][0],  # start_time
                'ENDTIME': time_table1[int(course['JSJC']) - 1][1],  # end_time
                'STARTWEEK': start_week,  # start_week
                'ENDWEEK': end_week,  # end_week
                'DETAIL': course['YPSJDD'],  # detail
                'WEEKINFO': course['SKZC'],  # week_info
                'WEEKDAY': course['SKXQ'],  # weekday
                'STARTSEQ': course['KSJC'],  # start_seq
                'ENDSEQ': course['JSJC']  # end_seq
            }
            new_data.append(new_course)
        save_data = {'courses': new_data}
        new_file = sid + term + 'schedule.json'
        filepath = os.path.join(config.json_save_path, new_file)
        with open(filepath, 'w', encoding="GBK") as f:
            f.write(json.dumps(save_data, ensure_ascii=False))
    except Exception:
        traceback.print_exc()


# ====================================================================================================
# ====================================================================================================
# ====================================================================================================


# save schedule in json type
def save_course(username, term, content, first_day="2023-02-20"):
    new_data = []
    for course in content['data']:
        weeks = course['SKZC']
        start_week = weeks.find('1') + 1
        end_week = weeks.rfind('1') + 1
        new_course = {
            'COURSENAME': course['KCM'],  # name
            'COURSENO': course['KCH'],  # number
            'TEACHERNAME': course['SKJS'],  # teacher
            'CLASSNO': course['SKBJ'],  # class_number
            'ROOMNO': course['JASMC'],  # location
            'STARTTIME': time_table1[int(course['KSJC']) - 1][0],  # start_time
            'ENDTIME': time_table1[int(course['JSJC']) - 1][1],  # end_time
            'STARTWEEK': start_week,  # start_week
            'ENDWEEK': end_week,  # end_week
            'DETAIL': course['YPSJDD'],  # detail
            'WEEKINFO': course['SKZC'],  # week_info
            'WEEKDAY': course['SKXQ'],  # weekday
            'STARTSEQ': course['KSJC'],  # start_seq
            'ENDSEQ': course['JSJC']  # end_seq
        }
        new_data.append(new_course)
    db.insert_courses(username, term, new_data, first_day)


# get schedule of specified week and return week schedule dict
def insert_courses_test(sid, username, term, first_day="2023-02-20"):
    filename = sid + term + "schedule.json"
    filepath = os.path.join(config.json_save_path, filename)
    if not os.path.exists(filepath):
        return {'data': 'please get your schedule first'}
    # make response data in specified format
    with open(filepath, 'r', encoding="GBK") as f:
        data = json.load(f)
    # add valid courses
    db.insert_courses(username, term, data['courses'], first_day)


def make_schedule_dict(username, eventID, date, time, name, description, isFinished):
    dict = {}
    dict["username"] = username
    dict["eventID"] = eventID
    dict["date"] = date
    dict["time"] = time
    dict["name"] = name
    dict["description"] = description
    dict["isFinished"] = isFinished
    return dict


# save schedule
def save_schedule(username, filename):
    course_list = save_course_schedule(username)
    # analyze ics file
    with open(filename, 'r', encoding='utf-8') as ics:
        data = ics.read()
        cal = icalendar.Calendar.from_ical(data)
        # eventID = 0
        schedule_list = []
        for event in cal.walk('VEVENT'):
            dtend = event.get("DTEND").dt
            date_str = dtend.strftime("%Y-%m-%d")
            time_str = dtend.strftime("%I:%M %p")  # %I: 小时(12小时制), %M: 分钟, %p: AM/PM
            name = event.get("SUMMARY")
            description = event.get("DESCRIPTION")
            isFinished = False
            schedule_list.append(make_schedule_dict(username, 0, date_str, time_str, name, description, isFinished
                                                    ))
        course_list.extend(schedule_list)
        save_list = sorted(course_list, key=lambda x: x['date'])
        for i, schedule in enumerate(save_list):
            schedule['eventID'] = i
        db.insert_schedules(save_list)


# save course as schedule
def save_course_schedule(username):
    result, courses_list = db.get_all_courses(username)
    courses_list = split_courses(courses_list)
    print(courses_list)
    schedule_list = []
    for course in courses_list:
        schedule_list.append(
            make_schedule_dict(username, 0, course['date'], course['startTime'], course['courseName'],
                               course['detail'], False
                               ))
    return schedule_list


def split_courses(courses_list):
    split_courses_list = []

    # 遍历每门课程
    for course in courses_list:
        course_name = course['courseName']
        start_time = course['startTime']
        week_info = course['weekInfo']
        week_day = int(course['weekDay'])
        detail = course['detail']
        first_day = datetime.datetime.strptime(course['firstDay'], '%Y-%m-%d')

        # 计算每门课程的具体上课日期
        for week in range(len(week_info)):
            if week_info[week] == '1':
                # 计算每周的日期偏移量
                offset = (week * 7) + (week_day - first_day.weekday() - 1)
                # 计算具体上课日期
                course_date = first_day + datetime.timedelta(days=offset)
                course_date_str = course_date.strftime('%Y-%m-%d')

                # 创建新的课程字典并添加到拆分后的课程列表中
                split_course = {
                    'courseName': course_name,
                    'startTime': start_time,
                    'date': course_date_str,
                    'detail': detail
                }
                split_courses_list.append(split_course)

    # 按日期排序课程列表
    sorted_courses_list = sorted(split_courses_list, key=lambda x: (x['date'], x['startTime']))

    return sorted_courses_list


# insert schedule
def insert_schedule_test(username):
    try:
        # todo: access website

        filename = "test.ics"
        save_schedule(username, config.schedule_path + filename)
    except Exception:
        traceback.print_exc()
        return False
    return True
