import os
import time
import traceback
from datetime import datetime, date
from flask import Flask, request, Response, send_file
from flask_cors import CORS
import json

import db
import execJs
import user
import config
import schedule

app = Flask(__name__)
CORS(app, resources=r"/*")
app.config['MAX_CONTENT_LENGTH'] = config.max_upload_size

# set database
app.config['SQLALCHEMY_DATABASE_URI'] = config.db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.db.app = app
db.db.init_app(app)
with app.app_context():
    # db.db.drop_all()
    # not influence tables existed
    db.db.create_all()


# make response
def get_response(data, status=200):
    class ComplexEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.strftime('%Y/%m/%d %H:%M:%S')
            elif isinstance(obj, date):
                return obj.strftime('%Y/%m/%d')
            else:
                return json.JSONEncoder.default(self, obj)

    return Response(json.dumps(data, cls=ComplexEncoder), status=status, mimetype='application/json')


# tests
@app.route("/test0/")
def test0():
    sid = request.args.get('sid', '')
    print("sid: " + sid)
    return get_response({'sid': sid}, 500)


# "http://localhost:5000/sleep"
@app.route("/sleep/")
def slp():
    for i in range(20):
        time.sleep(1)
        print("-----")
    return get_response({'sleep': "10s"}, 200)


# "http://localhost:5000/verify?sid=1120202079&pwd=xxx"
# verify
@app.route("/verify/", methods=['GET'])
def verify():
    sid = request.args.get('sid', '')
    pwd = request.args.get('pwd', '')
    if not (sid and pwd):
        return get_response({'msg': 'parameters invalid'}, 500)
    init_response = user.init(sid)
    # get parameters
    cookie = init_response['cookie']
    execution = init_response['execution']
    captcha = init_response['captcha']
    salt = init_response['salt']
    # calculate password
    encrypted_pwd = execJs.exec_encryptpassword(pwd, salt)
    try:
        verify_response = user.verify(sid, encrypted_pwd, execution, cookie, captcha)
    except Exception:
        traceback.print_exc()
        verify_response = False
    if verify_response:
        return get_response({'cookie': cookie, 'msg': 'success'}, 200)
    return get_response({'msg': 'error'}, 500)


# "http://localhost:5000/setname/?sid=1120202079&nickname=zkyquq"
# setname
@app.route("/setname/", methods=['GET'])
def set_name():
    sid = request.args.get('sid', '')
    nickname = request.args.get('nickname', '')
    if not (sid and nickname):
        return get_response({'msg': 'parameters invalid'}, 500)
    try:
        result = user.set_name(sid, nickname)
    except Exception:
        traceback.print_exc()
        result = False
    if result:
        return get_response({'msg': 'success'}, 200)
    return get_response({'msg': 'error'}, 500)


# "http://localhost:5000/getname/?sid=1120202079"
# getname
@app.route("/getname/", methods=['GET'])
def get_name():
    sid = request.args.get('sid', '')
    if not sid:
        return get_response({'msg': 'parameters invalid'}, 500)
    try:
        result = user.get_name(sid)
    except Exception:
        traceback.print_exc()
        result = None
    if result:
        return get_response({'nickname': result, 'msg': 'success'}, 200)
    return get_response({'msg': 'error'}, 500)


# term format: "2022-2023-2"
# "http://localhost:5000/geturl?sid=1120202079&cookie="
# "http://localhost:5000/geturl?term=2022-2023-1&sid=1120202079&cookie="
# getUrl
@app.route("/geturl/", methods=['GET'])
def get_url():
    sid = request.args.get('sid', '')
    cookie = request.args.get('cookie', '')
    term = request.args.get('term', '')
    if not (sid and cookie and term):
        return get_response({'msg': 'parameters invalid'}, 500)
    try:
        url = schedule.get_ics_url(cookie, sid, term)
    except Exception:
        traceback.print_exc()
        url = None
    if url:
        return get_response({'data': url, 'msg': 'success'}, 200)
    return get_response({'msg': 'error'}, 500)


# "http://localhost:5000/weekcourse?term=2022-2023-2&sid=1120202079&week=13"
@app.route("/weekcourse/", methods=['GET'])
def get_week_course():
    sid = request.args.get('sid', '')
    week = request.args.get('week', '')
    term = request.args.get('term', '')
    if not (sid and week and term):
        return get_response({'msg': 'parameters invalid'}, 500)
    try:
        response = schedule.get_week_schedule(sid, week, term)
    except Exception:
        traceback.print_exc()
        response = None
    if response:
        return get_response({'weekCourse': response, 'msg': 'success'}, 200)
    return get_response({'msg': 'error'}, 500)


# "http://localhost:5000/download?filename=11202020792022-2023-2schedule.json&type=json"
@app.route("/download/")
def download():
    file_name = request.args.get('filename')
    filetype = request.args.get('type')
    if not (file_name and filetype):
        return get_response({'msg': 'parameters invalid'}, 500)
    if filetype == 'ics':
        file_path = os.path.join(config.ics_save_path, file_name)
    elif filetype == 'json':
        file_path = os.path.join(config.json_save_path, file_name)
    else:
        return get_response({'msg': 'error'}, 500)
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return get_response({'msg': 'error'}, 500)


if __name__ == '__main__':
    # app.run(host="0.0.0.0", port=5000)

    app.run(debug=True)
    # app.run(debug=True, host="0.0.0.0", port=8000)
