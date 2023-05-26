import execjs

import config


def exec_encryptpassword(pwd, salt):
    # execute js file
    ctx = execjs.compile(open(config.psw_js_path, 'r', encoding='utf-8').read())
    sign = ctx.call('encryptPassword', pwd, salt)
    return sign
