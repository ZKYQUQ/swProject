import json
import os
import traceback
import config

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
