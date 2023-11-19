import json
import os
import traceback
from datetime import datetime, date

from flask import Flask, request, Response, send_file
from flask_cors import CORS

import config
import db
import execJs
import saver
import schedule
import user
import JWT

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


def make_response_dict(code, msg, data=None):
    return {"code": code, "msg": msg, "data": data}


# tests
# "http://localhost:5000/test0?username=1120202079"
@app.route("/test0/")
def test0():
    username = request.args.get('username', '')
    saver.save_course_schedule(username)
    return get_response("Success!",500)

# tests
# "http://localhost:5000/test_create_jwt?username=1120202079"
@app.route("/test_create_jwt/", methods=['GET'])
def test_create_jwt():
    username = request.args.get('username', '')
    token=JWT.create_token(username)
    return get_response(make_response_dict(200, "Jwt created!",token), 200)

# "http://localhost:5000/test_verify_jwt"
@app.route("/test_verify_jwt/", methods=['GET'])
def test_verify_jwt():
    auth = request.headers.get('Authorization')
    result,msg=JWT.verify_token(auth)
    if result:
        return get_response(make_response_dict(200, "Jwt veridied!"), 200)
    return get_response(make_response_dict(401,msg), 401)


# "http://localhost:5000/api/user/register"
@app.route("/api/user/register", methods=['POST'])
def user_register():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    if username and password:
        if db.user_register(username, password):
            return get_response(make_response_dict(200, "Register success!"), 200)
    return get_response(make_response_dict(400, "Register fail!"), 400)


# "http://localhost:5000/api/user/login"
@app.route("/api/user/login", methods=['POST'])
def user_login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    if username and password:
        if db.user_login(username, password):
            token = JWT.create_token(username)
            return get_response(make_response_dict(200, "Login success!",token), 200)
    return get_response(make_response_dict(400, "Login fail!"), 400)


# "http://localhost:5000/api/user/update"
@app.route("/api/user/update", methods=['POST'])
def user_update():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    sid = request.form.get('sid', '')
    spwd = request.form.get('spwd', '')
    nickname = request.form.get('nickname', '')

    auth = request.headers.get('Authorization')
    result, msg = JWT.verify_token(auth)
    if not result:
        return get_response(make_response_dict(401, msg), 401)

    if username:
        if db.user_update(username, password, sid, spwd, nickname):
            return get_response(make_response_dict(200, "Update success!"), 200)
    return get_response(make_response_dict(400, "Update fail!"), 400)


# "http://localhost:5000/api/courses"
@app.route("/api/courses", methods=['GET'])
def get_courses():
    username = request.args.get('username', '')
    week = request.args.get('week', '')
    term = request.args.get('term', '')

    auth = request.headers.get('Authorization')
    result, msg = JWT.verify_token(auth)
    if not result:
        return get_response(make_response_dict(401, msg), 401)

    if not (username and week and term):
        return get_response(make_response_dict(400, "Course parameters needed!"), 400)

    result, data = schedule.get_course(username, term, week)
    if not result:
        return get_response(make_response_dict(400, data), 400)
    return get_response(make_response_dict(200, "Get course success!", data), 200)


# "http://localhost:5000/api/insert_courses"
@app.route("/api/insert_courses", methods=['GET'])
def insert_courses():
    sid = request.args.get('sid', '')
    username = request.args.get('username', '')
    term = request.args.get('term', '')
    # print("sid: "+sid+"  "+"username: "+username+"  "+"term: "+term)

    auth = request.headers.get('Authorization')
    result, msg = JWT.verify_token(auth)
    if not result:
        return get_response(make_response_dict(401, msg), 401)

    if sid and username and term:
        saver.insert_courses_test(sid, username, term)
        return get_response(make_response_dict(200, "Course insert success!"), 200)
    return get_response(make_response_dict(400, "Course insert fail!"), 400)


# "http://localhost:5000/api/schedule"
@app.route("/api/schedule", methods=['GET'])
def get_schedule():
    username = request.args.get('username', '')

    auth = request.headers.get('Authorization')
    result, msg = JWT.verify_token(auth)
    if not result:
        return get_response(make_response_dict(401, msg), 401)

    if not username:
        return get_response(make_response_dict(400, "Schedule get parameters needed!"), 400)

    result, data = schedule.get_schedule(username)
    if not result:
        return get_response(make_response_dict(400, data), 400)
    return get_response(make_response_dict(200, "Get schedule success!", data), 200)


# "http://localhost:5000/api/schedule/update"
@app.route("/api/schedule/update", methods=['POST'])
def update_schedule():
    username = request.form.get('username', '')
    event = request.form.get('event', '')

    auth = request.headers.get('Authorization')
    result, msg = JWT.verify_token(auth)
    if not result:
        return get_response(make_response_dict(401, msg), 401)

    if not (username and event):
        return get_response(make_response_dict(400, "Schedule update parameters needed!"), 400)

    event = json.loads(event)
    result = schedule.update_schedule(username, event)
    if not result:
        return get_response(make_response_dict(400, "Schedule update fail!"), 400)
    result, data = schedule.get_schedule(username)
    if not result:
        return get_response(make_response_dict(400, data), 400)
    return get_response(make_response_dict(200, "Schedule update success!",data), 200)


# "http://localhost:5000/api/schedule/new"
@app.route("/api/schedule/new", methods=['POST'])
def insert_schedule():
    username = request.form.get('username', '')
    event = request.form.get('event', '')

    auth = request.headers.get('Authorization')
    result, msg = JWT.verify_token(auth)
    if not result:
        return get_response(make_response_dict(401, msg), 401)

    if not (username and event):
        return get_response(make_response_dict(400, "Schedule new parameters needed!"), 400)

    event = json.loads(event)
    result = schedule.insert_schedule(username, event)
    if not result:
        return get_response(make_response_dict(400, "Schedule new fail!"), 400)
    result, data = schedule.get_schedule(username)
    if not result:
        return get_response(make_response_dict(400, data), 400)
    return get_response(make_response_dict(200, "Schedule new success!",data), 200)


# "http://localhost:5000/api/schedule/finish"
@app.route("/api/schedule/finish", methods=['POST'])
def finish_schedule():
    username = request.form.get('username', '')
    eventID = request.form.get('eventID', '')

    auth = request.headers.get('Authorization')
    result, msg = JWT.verify_token(auth)
    if not result:
        return get_response(make_response_dict(401, msg), 401)

    if not (username and eventID):
        return get_response(make_response_dict(400, "Schedule finish parameters needed!"), 400)

    result = schedule.mark_schedule(username, eventID)
    if not result:
        return get_response(make_response_dict(400, "Schedule finish fail!"), 400)
    result, data = schedule.get_schedule(username)
    if not result:
        return get_response(make_response_dict(400, data), 400)
    return get_response(make_response_dict(200, "Schedule finish success!",data), 200)

# "http://localhost:5000/api/v2/user/verify_new/?sid=1120202079&pwd=xxx"
# verify
@app.route("/api/v2/user/verify_new/", methods=['GET'])
# @app.route("/verify/", methods=['GET'])
def verify_new():
    sid = request.args.get('sid', '')
    pwd = request.args.get('pwd', '')
    if not (sid and pwd):
        return get_response({'msg': 'parameters invalid'}, 500)
    init_response = user.init_new(sid)
    # get parameters
    execution = init_response['execution']
    salt = init_response['salt']
    captcha = init_response['captcha']
    cookie = init_response['cookie']
    # calculate password
    encrypted_pwd = execJs.exec_encryptpassword(pwd, salt)
    try:
        verify_response = user.verify_new(sid, encrypted_pwd, execution,cookie,captcha)
    except Exception:
        traceback.print_exc()
        verify_response = False
    if verify_response:
        return get_response({'msg': 'success'}, 200)
    return get_response({'msg': 'error'}, 500)


# ====================================================================================================
# ====================================================================================================
# ====================================================================================================


# "http://localhost:5000/verify?sid=1120202079&pwd=xxx"
# "http://localhost:5000/api/v2/user/verify/?sid=1120202079&pwd=xxx"
# verify
@app.route("/api/v2/user/verify/", methods=['GET'])
# @app.route("/verify/", methods=['GET'])
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


# term format: "2022-2023-2"
# "http://localhost:5000/geturl?sid=1120202079&cookie="
# "http://localhost:5000/geturl?term=2022-2023-1&sid=1120202079&cookie="
# "http://localhost:5000/api/v1/course/url/?term=2022-2023-1&sid=1120202079&cookie="
# getUrl
@app.route("/api/v1/course/url/", methods=['GET'])
# @app.route("/geturl/", methods=['GET'])
def get_url():
    sid = request.args.get('sid', '')
    cookie = request.args.get('cookie', '')
    term = request.args.get('term', '')
    print("request.args: " + str(request.args))
    print("app:cookie: " + cookie)
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
# "http://localhost:5000/api/v1/course/schedule/?term=2022-2023-2&sid=1120202079&week=13"
@app.route("/api/v1/course/schedule/", methods=['GET'])
# @app.route("/weekcourse/", methods=['GET'])
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
    # config.project_path=sys.argv[1]
    # config.project_path = os.environ.get('PROJECT_PATH')
    # config.ics_save_path = config.project_path + "save/ics"
    # config.json_save_path = config.project_path + "save/json"
    # config.psw_js_path = config.project_path + "EncryptPassword.js"

    # print(config.project_path)
    # print("input:  "+os.environ.get('PROJECT_PATH'))
    # print("project:  "+config.project_path)
    # print("json:  "+config.json_save_path)
    app.run(host="0.0.0.0", port=5000)
    # app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
