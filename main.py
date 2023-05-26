import json

import user
import webvpn
import execJs

if __name__ == '__main__':
    sid="1120202079"
    pwd="xxx"

    init_response=user.init(sid)
    print(init_response)
    cookie=init_response['cookie']
    execution=init_response['execution']
    captcha=init_response['captcha']
    salt=init_response['salt']

    encryptedPwd=execJs.exec_encryptpassword(pwd,salt)
    print(encryptedPwd)
    verify_response=user.verify(sid,encryptedPwd,execution,cookie,captcha)
    print(verify_response)
    schedule_dict=webvpn.get_schedule_term(cookie)
    print(schedule_dict)
    with open('schedule.json', 'w',encoding="GB2312") as f:
        # f.write(json.dumps(schedule_dict))
        f.write(json.dumps(schedule_dict, ensure_ascii=False))
