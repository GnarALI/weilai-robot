import json
import time
from datetime import datetime

import requests

from utils.logger import get_logger  # 导入自定义日志工具
from utils import request  #  utils/request.py 中统一管理
from dao.user_dao import UserDao

user_dao = UserDao()

headers = request.headers

# 初始化日志系统
loggers = get_logger()
get_task_log = loggers['get_task']
# 获取今日所有可抢藏品的名称、ID 和价格
def get_today_price():
    name_price = {}  # 例如：{'蛇来运转-Ⅰ代': '128.88'}
    data = {
        "pageSize": 100,
        "pageNum": 1,
        "productType": "BUYOUT",
        "collectionType": "2",
        "museumId": "-3"
    }
    try:
        response = requests.post("https://www.weilaiqiyuan.com/core/collection/public/search", json=data, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        today_list = response_json['data']['list']

        name_price.clear()  # 清空旧数据，防止残留

        for i in today_list:
            name = i['collectionDetailRes']['name']
            price = float(i['collectionDetailRes']['currentDayMaxPrice'])  # ✅ 转为 float
            name_price[name] = price

    except requests.exceptions.RequestException as e:
        get_task_log.error(f"请求出错: {e}")
        time.sleep(3)
        return get_today_price()

    except ValueError as e:
        get_task_log.error(f"响应内容不是有效的 JSON 格式: {e}")
        time.sleep(3)
        return get_today_price()



    return name_price  # ✅ 返回格式如：{"藏品名": float价格}

def generate_purchase_plan(balance: float, name_price: dict[str, float]) -> tuple[dict[str, int], str, float]:
    sorted_items = sorted(name_price.items(), key=lambda x: x[1], reverse=True)
    purchase_plan = {}
    total_spent = 0.0

    while True:
        bought_in_this_round = False

        for name, price in sorted_items:
            if balance < price:
                continue

            already_bought = purchase_plan.get(name, 0)
            can_buy = min(3 - already_bought, int(balance // price))

            if can_buy <= 0:
                continue

            purchase_plan[name] = already_bought + can_buy
            balance -= price * can_buy
            total_spent += price * can_buy
            bought_in_this_round = True

        if not bought_in_this_round:
            break

    # 构造用户可读的 summary 字符串
    summary_lines = []
    for name, count in purchase_plan.items():
        price = name_price[name]
        line = f"{name} × {count} = ¥{price * count:.2f}"
        summary_lines.append(line)

    plan_summary_str = "\n".join(summary_lines)
    remaining_balance = round(balance, 2)

    return purchase_plan, plan_summary_str, remaining_balance

def get_fixed_task_time():
    today = datetime.now().strftime("%Y/%m/%d")
    return f"{today} 14:59:57"

def get_user_task(phone):
    name_price = get_today_price()
    name_price = {name: price for name, price in name_price.items() if price >= 100}

    user = user_dao.get_user_by_phone(phone)

    if user is not None:
        balance = float(user.get("balance") or 0)
        task, task_msg, remaining_balance = generate_purchase_plan(balance, name_price)
    else:
        return "未找到用户，无法生成任务"

    # 如果没有生成任何任务，提前返回，不做任何数据库更新
    if not task:
        return f"📭 当前钱包余额 ¥{balance:.2f}，未生成任何抢购任务。"

    # 1. 更新任务内容
    task_json = json.dumps(task, ensure_ascii=False)
    user_dao.update_task_by_phone(phone, task_json)

    # 2. 更新任务时间
    fixed_time = get_fixed_task_time()
    user_dao.update_task_time_by_phone(phone, fixed_time)

    # 3. 更新 VIP 标记
    user_dao.update_is_vip_by_phone(phone)

    # 4. 返回最终结果文本
    results = (
        f"钱包余额：¥{balance:.2f} 元\n\n"
        f"本次抢购任务：\n{task_msg}\n\n"
        f"预计抢购后剩余余额：¥{remaining_balance:.2f} 元"
    )
    return results

