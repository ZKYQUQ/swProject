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


# set nickname
def set_name(sid, nickname):
    if db.check_user(sid):
        db.set_nickname(sid, nickname)
    else:
        db.insert_user(sid, nickname)
    return True


# get nickname
def get_name(sid):
    if db.check_user(sid):
        nickname = db.get_nickname(sid)
    else:
        nickname = None
    return nickname
