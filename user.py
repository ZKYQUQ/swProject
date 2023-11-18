import db
import base64

import webvpn


# initialization
def init(sid):
    dic = webvpn.init_login()
    if webvpn.need_captcha(sid):
        img = webvpn.get_captcha(dic['cookie'])
        dic['captcha'] = base64.b64encode(img).decode()
    else:
        dic['captcha'] = False
    return dic


# verification
def verify(username, password, execution, cookie, captcha=""):
    if webvpn.login(username, password, execution, cookie, captcha):
        return True
    return False


# ====================================================================================================
# ====================================================================================================
# ====================================================================================================


# initialization
def init_new(sid):
    dic = webvpn.init_login_new()
    if webvpn.need_captcha_new(sid):
        img = webvpn.get_captcha_new(dic['cookie'])
        dic['captcha'] = base64.b64encode(img).decode()
    else:
        dic['captcha'] = False
    print(dic)
    return dic


# verification
def verify_new(username, password, execution,cookie, captcha=""):
    if webvpn.login_new(username, password, execution,cookie,captcha):
        return True
    return False