import time
import requests
import threading
import random
from utils.logger import get_logger  # 导入自定义日志工具
from utils import request  #  utils/request.py 中统一管理

# 初始化日志系统
logger, success_logger = get_logger()

# 抢购请求接口地址
url = "https://www.weilaiqiyuan.com/core/buyout_products/buy/order/bulk"

# 公共请求头（基础结构，后续每次请求前会附加 token 和伪造 IP）
headers = request.headers

# 配置：每个线程的请求次数（理论上为无限，直到任务成功或中断）
loop_count = 9999999

# 每个任务开启的并发线程数量
thread_count = 10

# 商品名称到 ID、价格的映射
name_id = {}           # 例如：{'蛇来运转-Ⅰ代': '890123'}
name_price = {}        # 例如：{'蛇来运转-Ⅰ代': '128.88'}

# 手机号到 token（Authorization）、支付密码的映射
phone_authorization = {}   # 例如：{'19912345678': 'eyJhbGci...'}
phone_password = {}        # 例如：{'19912345678': '123456'}

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

    for _ in range(loop_count):
        print(f"[*][send_request][{data['name']}-{data['id']}]第 {_+1} 次请求")
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
                logger.error(f"[{data['phone']}]{data['name']}请求响应码异常: {response.status_code}, 内容: {response.text}")
                print(f"[send_request]请求响应码异常{response}")
                continue

            response_json = response.json()

            # 这几个状态码通常代表未成功锁单，跳过
            if response_json.get('code') in ['10', '0', '500']:
                print(f"[send_request]未成功锁单{response_json}")
                continue
            print(f"[send_request]----成功锁单----{response_json}")
            process_response(data, response_json, request_header)


        except Exception as e:
            logger.error(f"[{data['phone']}]请求异常: {e}")


# 处理锁单响应结果
def process_response(data: dict, response_json: dict, request_header: dict):
    if response_json.get('code') == '200':
        order_no = response_json['data']['orderNo']
        success_logger.info(f"[+][{data['phone']}]{data['name']}锁单成功, 数量: {len(response_json['data']['childOrders'])}, 订单号: {order_no}")
        print(f"[process_response]锁单成功{response_json}")
        order(data, order_no, request_header)
    else:
        logger.info(f"[*][{data['phone']}]{data['name']}响应码: {response_json.get('code')}, 内容: {response_json}")
        print(f"[process_response]锁单失败{response_json}")

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

    for _ in range(20):  # 尝试最多支付 20 次
        try:
            response = requests.post(
                "https://www.weilaiqiyuan.com/core/buyout_products/pay/order",
                json=payload,
                headers=request_header,
                timeout=3
            )
            response_json = response.json()
            print(f"[order]支付第 {_ + 1} 次尝试，响应：{response_json}")
            if response_json.get('code') == "200":
                success_logger.info(f"[*][{data['phone']}]{data['name']}支付成功, 订单号: {order_no}")
                print(f"支付成功{response_json}")
                return
            else:
                success_logger.warning(f"[-][{data['phone']}]{data['name']}支付失败, 订单号: {order_no}, 内容: {response_json}")
                print(f"[order]支付失败{response_json}")
                return
        except Exception as e:
            success_logger.error(f"[{data['phone']}]{data['name']}支付异常: {e}")
            print(f"[order]支付异常{e}")



# 获取今日所有可抢藏品的名称、ID 和价格
def get_today_price():
    data = {"pageSize": 100, "pageNum": 1, "productType": "BUYOUT","collectionType":"2","museumId":"-3"}
    try:
        response = requests.post("https://www.weilaiqiyuan.com/core/collection/public/search", json=data, headers=headers)
        response.raise_for_status()
        # 解析响应为 JSON 格式
        response_json = response.json()
        today_list = response_json['data']['list']
        # data_list = []
        for i in today_list:
            name_id[i['collectionDetailRes']['name']] = i['collectionDetailRes']['id']
            name_price[i['collectionDetailRes']['name']] = i['collectionDetailRes']['currentDayMaxPrice']
    except requests.exceptions.RequestException as e:
        logger.error(f"请求出错: {e}")
        time.sleep(3)
        get_today_price()
    except ValueError as e:
        logger.error(f"响应内容不是有效的 JSON 格式: {e}")
        time.sleep(3)
        get_today_price()
    # logging.info(name_price)




# 根据任务行数据生成可执行任务
def generate_task(task_lines: list[str]) -> list[dict]:
    """
    task_lines 示例：
    [
        "19912345678-蛇来运转-1",
        "18888888888-魔礼青-2"
    ]
    """
    tasks = []
    for line in task_lines:
        phone, name, count = line.strip().split("-")

        # 商品名映射（支持简写）
        name = {
            '蛇来运转': '蛇来运转-Ⅰ代',
            '魔礼青': '四大天王-魔礼青',
            '魔礼海': '四大天王-魔礼海',
            '魔礼红': '四大天王-魔礼红',
            '魔礼寿': '四大天王-魔礼寿',
            '龙': '屋脊兽·龙',
            '貔貅': '山海经·貔貅',
            '青鸾': '山海经·青鸾',
        }.get(name, name)

        if phone in phone_authorization:
            task = {
                "name": name,
                "id": name_id.get(name, ""),
                "buyCount": count,
                "maxPrice": name_price.get(name, "99999"),
                "authorization": phone_authorization[phone],
                "phone": phone,
                "pwd": phone_password.get(phone, '')
            }
            tasks.append(task)
    return tasks

# 启动所有任务
def start_task(authorization_list: list[str], task_lines: list[str]):
    """
    :param authorization_list: ['19912345678:token1:123456', '18888888888:token2:888888']
    :param task_lines: ['19912345678-蛇来运转-1', '18888888888-魔礼青-2']
    """
    # 加载手机号与 Token、支付密码
    for auth in authorization_list:
        phone, token, pwd = auth.strip().split(":")
        phone_authorization[phone] = token
        phone_password[phone] = pwd

    # 获取当日可抢藏品信息
    get_today_price()

    # 生成任务列表
    tasks = generate_task(task_lines)
    logger.info(f"准备启动 {len(tasks)} 条任务")
    print(f"准备启动 {len(tasks)} 条任务")

    # 多线程并发执行
    threads = []
    for task in tasks:
        for _ in range(thread_count):
            t = threading.Thread(target=send_request, args=(task,))
            threads.append(t)
            t.start()

    # 等待所有线程结束
    for t in threads:
        t.join()

    logger.info("[*] 所有请求完成。")
    print("所有请求完成。")
