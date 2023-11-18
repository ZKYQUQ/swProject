import json
import traceback

import requests
from bs4 import BeautifulSoup as bs

import config
import saver

# # login
# base_url = "https://webvpn.bit.edu.cn"
# login_url = base_url + \
#             "/https/77726476706e69737468656265737421fcf84695297e6a596a468ca88d1b203b/authserver/login?service=https%3A%2F%2Fwebvpn.bit.edu.cn%2Flogin%3Fcas_login%3Dtrue"
# need_captcha_url = base_url + \
#                    "/https/77726476706e69737468656265737421fcf84695297e6a596a468ca88d1b203b/authserver/checkNeedCaptcha.htl"
# get_captcha_url = base_url + \
#                   "/https/77726476706e69737468656265737421fcf84695297e6a596a468ca88d1b203b/authserver/getCaptcha.htl"
#
# # schedule
# schedule_init_url = base_url + \
#                     "/http/77726476706e69737468656265737421faef5b842238695c720999bcd6572a216b231105adc27d/jwapp" \
#                     "/sys/funauthapp/api/getAppConfig/wdkbby-5959167891382285.do"
# schedule_lang_url = base_url + \
#                     "/http/77726476706e69737468656265737421faef5b842238695c720999bcd6572a216b231105adc27d/jwapp" \
#                     "/i18n.do?appName=wdkbby&EMAP_LANG=zh"
# schedule_now_term_url = base_url + \
#                         "/http/77726476706e69737468656265737421faef5b842238695c720999bcd6572a216b231105adc27d/jwapp" \
#                         "/sys/wdkbby/modules/jshkcb/dqxnxq.do"
# schedule_all_terms_url = base_url + \
#                          "/http/77726476706e69737468656265737421faef5b842238695c720999bcd6572a216b231105adc27d/jwapp" \
#                          "/sys/wdkbby/modules/jshkcb/xnxqcx.do"
# schedule_url = base_url + \
#                "/http/77726476706e69737468656265737421faef5b842238695c720999bcd6572a216b231105adc27d/jwapp" \
#                "/sys/wdkbby/modules/xskcb/cxxszhxqkb.do"
# schedule_date_url = base_url + \
#                     "/http/77726476706e69737468656265737421faef5b842238695c720999bcd6572a216b231105adc27d/jwapp" \
#                     "/sys/wdkbby/wdkbByController/cxzkbrq.do"



# redirection
def redirection(url, head={}, data={}):
    r = requests.post(url, data, headers=head, allow_redirects=False)
    while r.status_code == 302:
        url = r.headers['Location']
        if url[0] == '/':
            url = base_url + url
        # print(url)
        r = requests.get(url, headers=head, allow_redirects=False)
    return r

# init_login
def init_login():
    r = redirection(login_url)
    soup = bs(r.text, 'html.parser')
    x = soup.find(id="pwdFromId")
    salt = x.find(id="pwdEncryptSalt")['value']
    execution = x.find(id="execution")['value']
    cookie = r.headers['Set-Cookie']
    return {'salt': salt, 'execution': execution, 'cookie': cookie}


# captcha requirement check
def need_captcha(sid):
    r = redirection(need_captcha_url + "?username=" + sid)
    return json.loads(r.text)['isNeed']


# get captcha
def get_captcha(cookie):
    r = redirection(get_captcha_url, head={'Cookie': cookie})
    return r.content


# login
def login(username, password, execution, cookie, captcha=""):
    head = {"Cookie": cookie}
    data = {
        'username': username,
        'password': password,
        'execution': execution,
        'captcha': captcha,
        '_eventId': "submit",
        'cllt': "userNameLogin",
        'dllt': "generalLogin",
        'lt': "",
        'rememberMe': "true",
    }
    r = redirection(login_url, data=data, head=head)
    if r.status_code != 200 or "帐号登录或动态码登录" in r.text:
        return False
    return True


# get schedule of specified term
def get_schedule_term(sid, cookie, term=''):
    # initialization
    redirection(schedule_init_url, head={'Cookie': cookie})
    redirection(schedule_lang_url, head={'Cookie': cookie})

    # set now term if param term is empty
    r = redirection(schedule_all_terms_url, head={'Cookie': cookie})
    print(r.content)
    if not term:
        r = redirection(schedule_now_term_url, head={'Cookie': cookie})
        term = r.json()['datas']['dqxnxq']['rows'][0]['DM']  # "2022-2023-2"
    # get first day of the term
    r = redirection(schedule_date_url, head={'Cookie': cookie},
                    data={'requestParamStr': '{"XNXQDM":"' + term + '","ZC":"1"}'})
    for i in r.json()['data']:
        if i['XQ'] == 1:
            first_day = i['RQ']

    print(r.content)
    print("term: " + term + "  cookie:" + cookie)
    # get schedule
    r = redirection(schedule_url, head={'Cookie': cookie}, data={'XNXQDM': term})
    print(r.content)
    schedule_list = r.json()['datas']['cxxszhxqkb']['rows']
    save_content = {'data': schedule_list}
    # save schedule in json
    # saver.save_json(sid, save_content)
    saver.save_json(sid, term, save_content)
    return {
        'first_day': first_day,
        'data': schedule_list,
    }


# ====================================================================================================
# ====================================================================================================
# ====================================================================================================


# login
base_url = "https://jxzxehallapp.bit.edu.cn"
login_base_url = "https://login.bit.edu.cn"
login_url = "https://login.bit.edu.cn/authserver/login"
need_captcha_url = "https://login.bit.edu.cn/authserver/checkNeedCaptcha.htl"
get_captcha_url = "https://login.bit.edu.cn/authserver/getCaptcha.htl"

# schedule
schedule_init_url = "https://jxzxehallapp.bit.edu.cn/jwapp/sys/funauthapp/api/getAppConfig/wdkbby-5959167891382285.do"
schedule_lang_url = "https://jxzxehallapp.bit.edu.cn/jwapp/i18n.do?appName=wdkbby&EMAP_LANG=zh"
schedule_now_term_url = "https://jxzxehallapp.bit.edu.cn/jwapp/sys/wdkbby/modules/jshkcb/dqxnxq.do"
schedule_all_terms_url = "https://jxzxehallapp.bit.edu.cn/jwapp/sys/wdkbby/modules/jshkcb/xnxqcx.do"
schedule_url = "https://jxzxehallapp.bit.edu.cn/jwapp/sys/wdkbby/modules/xskcb/cxxszhxqkb.do"
schedule_date_url = "https://jxzxehallapp.bit.edu.cn/jwapp/sys/wdkbby/wdkbByController/cxzkbrq.do"


# # redirection
# def redirection(url, head={}, data={}):
#     r = requests.post(url, data, headers=head, allow_redirects=False)
#     while r.status_code == 302:
#         url = r.headers['Location']
#         if url[0] == '/':
#             url = base_url + url
#         # print(url)
#         r = requests.get(url, headers=head, allow_redirects=False)
#     return r


def redirection_login(url, head={}, data={}):
    r = requests.post(url, data, headers=head, allow_redirects=False)
    while r.status_code == 302:
        url = r.headers['Location']
        if url[0] == '/':
            url = login_base_url + url
        # print(url)
        r = requests.get(url, headers=head, allow_redirects=False)
    return r


# init_login
def init_login_new():
    r = redirection_login(login_url)
    soup = bs(r.text, 'html.parser')
    x = soup.find(id="pwdFromId")
    salt = x.find(id="pwdEncryptSalt")['value']
    execution = x.find(id="execution")['value']
    # cookie = r.headers['Set-Cookie']
    cookie = r.headers.get('Set-Cookie')
    return {'salt': salt, 'execution': execution, 'cookie': cookie}


# captcha requirement check
def need_captcha_new(sid):
    r = redirection(need_captcha_url + "?username=" + sid)
    return json.loads(r.text)['isNeed']


# get captcha
def get_captcha_new(cookie):
    r = redirection(get_captcha_url, head={'Cookie': cookie})
    return r.content

# login
def login_new(username, password, execution,cookie,captcha=""):
    head = {"Cookie": cookie}

    data = {
        'username': username,
        'password': password,
        'execution': execution,
        'captcha': captcha if captcha!=False else "",
        '_eventId': "submit",
        'cllt': "userNameLogin",
        'dllt': "generalLogin",
        'lt': "",
        'rememberMe': "true",
    }
    print("data: "+str(data))
    print("cookie: " + str(head))
    # 下面可以暂时注释掉，太多次登录失败会被冻结
    r = redirection_login(login_url, data=data,head=head)
    print(r.text)
    if r.status_code != 200 or "帐号登录或动态码登录" in r.text:
        return False
    return True




# get schedule of specified term
def get_course(username, cookie, term=''):
    try:
        # initialization
        redirection(schedule_init_url, head={'Cookie': cookie})
        redirection(schedule_lang_url, head={'Cookie': cookie})

        # set now term if param term is empty
        r = redirection(schedule_all_terms_url, head={'Cookie': cookie})
        if not term:
            r = redirection(schedule_now_term_url, head={'Cookie': cookie})
            term = r.json()['datas']['dqxnxq']['rows'][0]['DM']  # "2022-2023-2"
        # get first day of the term
        r = redirection(schedule_date_url, head={'Cookie': cookie},
                        data={'requestParamStr': '{"XNXQDM":"' + term + '","ZC":"1"}'})
        for i in r.json()['data']:
            if i['XQ'] == 1:
                first_day = i['RQ']

        # get schedule
        r = redirection(schedule_url, head={'Cookie': cookie}, data={'XNXQDM': term})
        schedule_list = r.json()['datas']['cxxszhxqkb']['rows']
        save_content = {'data': schedule_list}
        saver.save_course(username, term, save_content)
    except Exception:
        traceback.print_exc()
        return False
    return True


# get schedule from website
def get_schedule(username):
    try:
        # todo: access website

        filename = "test.ics"
        saver.save_schedule(username, config.schedule_path + filename)
    except Exception:
        traceback.print_exc()
        return False
    return True


# 乐学主页
lexueMainUrl="https://lexue.bit.edu.cn"

# 乐学导出课程表页面
lexueCalendarExportUrl="https://lexue.bit.edu.cn/calendar/export.php"
