import datetime

import jwt
from jwt import exceptions

# 构造header
headers = {
    'typ': 'jwt',
    'alg': 'HS256'
}

# 密钥
SALT = 'iv%i6xo7l8_t9bf_u!8#g#m*)*+ej@bek6)(@u3kh*42+unjv='


def create_token(username):
    # 构造payload
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)  # 超时时间
    }
    result = jwt.encode(payload=payload, key=SALT, algorithm="HS256", headers=headers)
    return result


def verify_token(auth):
    """
    1.获取请求头Authorization中的token
    2.判断是否以 Bearer开头
    3.使用jwt模块进行校验
    4.判断校验结果,成功就提取token中的载荷信息,赋值给g对象保存
    """
    if auth and auth.startswith('Bearer '):
        "提取token 0-6 被Bearer和空格占用 取下标7以后的所有字符"
        token = auth[7:]
        "校验token"
        try:
            "判断token的校验结果"
            jwt.decode(token, SALT, algorithms=['HS256'])
        except exceptions.ExpiredSignatureError:  # 'token已失效'
            return False, 'token已失效'
        except jwt.DecodeError:  # 'token认证失败'
            return False, 'token认证失败'
        except jwt.InvalidTokenError:  # '非法的token'
            return False, '非法的token'
        return True, "认证成功"
    return False, 'token认证失败'
