# login_manager.py
import requests
import time
import datetime
import logging

from utils import request


def get_token_by_login(phone: str, sms: str) -> tuple:
    """
    使用手机号和短信验证码登录，获取 token。
    返回值：
    - 成功：返回 token 字符串
    - 失败：返回空字符串 ""
    """
    login_data = {
        "loginName": phone,
        "smsCode": sms
    }

    try:
        response = requests.post(
            "https://www.weilaiqiyuan.com/core/cuser/public/login",
            json=login_data,
            headers=request.headers,
            timeout=3
        )
        response.raise_for_status()
        response_json = response.json()

        if response_json.get('code') != '200':
            logging.warning(f"[{phone}] 登陆失败 → {response_json}")
            return None,"登录失败"

        token = response_json['data']['token']
        expire_ts_ms = int(response_json['data']['expireTime'])

        logging.info(f"[{phone}] 登录成功，Token: {token}")
        logging.info(f"[{phone}] Token 过期时间戳（ms）: {expire_ts_ms}")

        expire_time_obj = datetime.datetime.fromtimestamp(expire_ts_ms / 1000)
        expire_time_str = expire_time_obj.strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"[{phone}] Token 过期时间（北京时间）: {expire_time_str}")

        return token, expire_time_str

    except requests.exceptions.RequestException as e:
        logging.error(f"[{phone}] 请求出错: {e}")

        return None,e

    except ValueError as e:
        logging.error(f"[{phone}] 响应不是合法 JSON: {e}")
        return None,e
