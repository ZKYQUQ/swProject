import requests
import json
from bs4 import BeautifulSoup as bs

import saver

base_url = "https://webvpn.bit.edu.cn"
login_url = base_url + \
            "/https/77726476706e69737468656265737421fcf84695297e6a596a468ca88d1b203b/authserver/login?service=https%3A%2F%2Fwebvpn.bit.edu.cn%2Flogin%3Fcas_login%3Dtrue"
need_captcha_url = base_url + \
                   "/https/77726476706e69737468656265737421fcf84695297e6a596a468ca88d1b203b/authserver/checkNeedCaptcha.htl"
get_captcha_url = base_url + \
                  "/https/77726476706e69737468656265737421fcf84695297e6a596a468ca88d1b203b/authserver/getCaptcha.htl"

# schedule
schedule_init_url = base_url + \
                    "/http/77726476706e69737468656265737421faef5b842238695c720999bcd6572a216b231105adc27d/jwapp/sys/funauthapp/api/getAppConfig/wdkbby-5959167891382285.do"
schedule_lang_url = base_url + \
                    "/http/77726476706e69737468656265737421faef5b842238695c720999bcd6572a216b231105adc27d/jwapp/i18n.do?appName=wdkbby&EMAP_LANG=zh"
schedule_now_term_url = base_url + \
                        "/http/77726476706e69737468656265737421faef5b842238695c720999bcd6572a216b231105adc27d/jwapp/sys/wdkbby/modules/jshkcb/dqxnxq.do"
schedule_all_terms_url = base_url + \
                         "/http/77726476706e69737468656265737421faef5b842238695c720999bcd6572a216b231105adc27d/jwapp/sys/wdkbby/modules/jshkcb/xnxqcx.do"
schedule_url = base_url + \
               "/http/77726476706e69737468656265737421faef5b842238695c720999bcd6572a216b231105adc27d/jwapp/sys/wdkbby/modules/xskcb/cxxszhxqkb.do"
schedule_date_url = base_url + \
                    "/http/77726476706e69737468656265737421faef5b842238695c720999bcd6572a216b231105adc27d/jwapp/sys/wdkbby/wdkbByController/cxzkbrq.do"


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
    # save schedule in json
    # saver.save_json(sid, save_content)
    saver.save_json(sid, term, save_content)
    return {
        'first_day': first_day,
        'data': schedule_list,
    }
