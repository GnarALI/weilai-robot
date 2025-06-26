# login_manager.py
import random
import requests
from utils.logger import get_logger  # 导入自定义日志工具
from utils import request

loggers = get_logger()
check_token_logger = loggers['check_token']

def generate_random_ipv4():
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))

def check_login_token(phone: str, token: str):
    fake_ip = generate_random_ipv4()

    # 每次调用时复制 headers，避免污染全局
    headers = request.headers.copy()
    headers.update({
        "Authorization": token,
        "X-Token": token,
        "X-Forwarded-For": fake_ip,
        "CLIENT_IP": fake_ip,
        "REMOTE_ADDR": fake_ip,
        "Via": fake_ip
    })

    try:
        response = requests.post(
            "https://api-sc.weilaiqiyuan.com/core/cuser/my",
            headers=headers,
            timeout=3
        )
        response.raise_for_status()
        response_json = response.json()

        if response_json.get('code') == '200':
            check_token_logger.info(f"[{phone}] token有效: {response_json}")
            return 100
        else:
            check_token_logger.warning(f"[{phone}] token失效: {response_json}")
            return -1

    except requests.exceptions.RequestException as e:
        check_token_logger.error(f"[{phone}] 请求出错: {e}")
        return -2

    except ValueError as e:
        check_token_logger.error(f"[{phone}] 响应不是合法 JSON: {e}")
        return -3
