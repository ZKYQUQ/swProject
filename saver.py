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


# save schedule in icalendar type
def save_ics(filename, data):
    with open(os.path.join(config.ics_save_path, filename), "wb") as f:
        f.write(data)
    return filename


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
def save_course(username, term, content):
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
    db.insert_courses(username, term, new_data)


# get schedule of specified week and return week schedule dict
def insert_courses_test(sid, username, term):
    filename = sid + term + "schedule.json"
    filepath = os.path.join(config.json_save_path, filename)
    if not os.path.exists(filepath):
        return {'data': 'please get your schedule first'}
    # make response data in specified format
    with open(filepath, 'r', encoding="GBK") as f:
        data = json.load(f)
    # add valid courses
    db.insert_courses(username, term, data['courses'])


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
    # analyze ics file
    with open(filename, 'r', encoding='utf-8') as ics:
        data = ics.read()
        cal = icalendar.Calendar.from_ical(data)
        eventID = 0
        schedule_list = []
        for event in cal.walk('VEVENT'):
            dtend = event.get("DTEND").dt
            date_str = dtend.strftime("%Y-%m-%d")
            time_str = dtend.strftime("%I:%M %p")  # %I: 小时(12小时制), %M: 分钟, %p: AM/PM
            name = event.get("SUMMARY")
            description = event.get("DESCRIPTION")
            isFinished = False
            schedule_list.append(make_schedule_dict(username, eventID, date_str, time_str, name, description, isFinished
                                                    ))
            eventID = eventID + 1
        db.insert_schedules(schedule_list)


