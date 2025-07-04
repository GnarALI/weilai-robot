import time
import requests
import threading
import random
from dao.user_dao import UserDao
from utils.logger import get_logger  # 导入自定义日志工具
from utils import request  #  utils/request.py 中统一管理
#初始化数据库
user_dao = UserDao()

# 初始化日志系统
loggers = get_logger()
main_log = loggers['main']
request_log = loggers['request']
process_log = loggers['process']
order_log = loggers['order']
success_log = loggers['success']

# 抢购请求接口地址
url = "https://www.weilaiqiyuan.com/core/buyout_products/buy/order/bulk"

# 公共请求头（基础结构，后续每次请求前会附加 token 和伪造 IP）
headers = request.headers


# 生成随机 IPv4 地址用于伪造请求来源
def generate_random_ipv4():
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))

# 发送下单请求（并伪造 IP）
def send_request(data: dict):


    """
    data 示例结构:
    {
        'name': '蛇来运转-Ⅰ代',
        'id': '商品ID',
        'buyCount': '1',
        'maxPrice': '128.00',
        'pwd': '支付密码'
    }
    """
    data_send = {
        "name": data['name'],
        "id": data['id'],
        "buyCount": data['buyCount'],
        "maxPrice": data['maxPrice'],
        "authorization": data['authorization']
    }
    #请求 1000 次，失败后重试
    for _ in range(500):
        try:
            # 构造伪造 IP 头部
            fake_ip = generate_random_ipv4()
            request_header = headers.copy()
            request_header.update({
                "Authorization": data['authorization'],
                "X-Token": data['authorization'],
                "X-Forwarded-For": fake_ip,
                "CLIENT_IP": fake_ip,
                "REMOTE_ADDR": fake_ip,
                "Via": fake_ip
            })

            response = requests.post(url, json=data_send, headers=request_header, timeout=30)

            if response.status_code != 200:
                request_log.warning(f"[{data['phone']}]{data['name']}请求响应码异常: {response.status_code}, 内容: {response.text}")
                continue

            response_json = response.json()

            # 这几个状态码通常代表未成功锁单，跳过
            if response_json.get('code') in ['10', '0', '500']:
                request_log.info(
                    f"[{data['phone']}]{data['name']}请求响应码异常: {response.status_code}, 内容: {response.text}")
                continue
            process_response(data, response_json, request_header)

        except Exception as e:
            request_log.error(f"[{data['phone']}]请求异常: {e}")

# 处理锁单响应结果
def process_response(data: dict, response_json: dict, request_header: dict):

    if response_json.get('code') == '200':
        order_no = response_json['data']['orderNo']
        process_log.info(f"[+][{data['phone']}]{data['name']}锁单成功, 数量: {len(response_json['data']['childOrders'])}, 订单号: {order_no}")
        order(data, order_no, request_header)
    else:
        process_log.warning(f"[*][{data['phone']}]{data['name']}响应码: {response_json.get('code')}, 内容: {response_json}")

# 提交支付订单
def order(data: dict, order_no: str, request_header: dict):
    """
    根据锁单后的 order_no 发起支付请求
    """
    payload = {
        "authorization": data['authorization'],
        "id": order_no,
        "isBalanceDiscount": 1,
        "payType": 7,
        "pwd": data['pwd']
    }

    for _ in range(100):  # 尝试最多支付 100 次
        try:
            response = requests.post(
                "https://www.weilaiqiyuan.com/core/buyout_products/pay/order",
                json=payload,
                headers=request_header,
                timeout=3
            )
            response_json = response.json()
            if response_json.get('code') == "200":
                # 获取当前用户的成功任务记录
                user = user_dao.get_user_by_phone(data['phone'])
                # 如果已有成功任务记录，则拼接到当前记录中，否则只是记录当前任务
                user_logs = f"[*][{data['phone']}]{data['name']}支付成功, 订单号: {order_no}"
                # 如果之前有成功记录，拼接旧的记录
                if user and user.get("success_task"):
                    user_logs = f"{user['success_task']}\n{user_logs}"
                # 记录日志
                success_log.info(user_logs)
                # 更新数据库中的成功任务记录
                user_dao.update_success_task_by_phone(data['phone'], user_logs)
                user_dao.update_task_status100_by_phone(data['phone'])
                return
            else:
                order_log.warning(f"[-][{data['phone']}]{data['name']}支付失败, 订单号: {order_no}, 内容: {response_json}")
                return
        except Exception as e:
            order_log.error(f"[{data['phone']}]{data['name']}支付异常: {e}")








