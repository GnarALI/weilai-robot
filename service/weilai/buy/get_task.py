import time
import requests
from utils.logger import get_logger  # 导入自定义日志工具
from utils import request  #  utils/request.py 中统一管理
from dao.user_dao import UserDao  # 导入用户数据库操作类
import datetime

user_dao = UserDao()

# 商品名称到 ID、价格的映射
name_id = {}           # 例如：{'蛇来运转-Ⅰ代': '890123'}
name_price = {}        # 例如：{'蛇来运转-Ⅰ代': '128.88'}

# 公共请求头（基础结构，后续每次请求前会附加 token 和伪造 IP）
headers = request.headers

# 初始化日志系统
loggers = get_logger()
get_task_log = loggers['get_task']


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
        get_task_log.error(f"请求出错: {e}")
        time.sleep(3)
        get_today_price()
    except ValueError as e:
        get_task_log.error(f"响应内容不是有效的 JSON 格式: {e}")
        time.sleep(3)
        get_today_price()
    # get_task_log.info(name_price)


# 根据数据库取得当日任务，和执行时间
def get_today_task_detail() -> list[dict]:
    """
    1. 从数据库获取当天的任务用户记录
    2. 解析每个用户的任务字符串
    3. 返回标准任务明细列表（供抢购用）
    """
    today_str = datetime.datetime.now().strftime("%Y/%m/%d")
    users = user_dao.get_users_by_task_date(today_str)

    user_lines = []
    for user in users:
        phone = user.get("phone")
        token = user.get("token")
        pwd = user.get("pay_pwd")
        is_vip = user.get("is_vip")
        task_time = user.get("task_time")
        task = user.get("task")  # json 字符串

        if not all([phone, token, pwd, task_time, task]):
            continue

        # 拼接成统一格式：手机号-token-密码-任务时间-任务json
        user_line = f"{phone}-{pwd}-{is_vip}-{task_time}-{task}-{token}"
        user_lines.append(user_line)

    result = parse_tasks(user_lines)

    # ⭐ 对结果排序：VIP 优先（is_vip=1的排前面）
    result.sort(key=lambda x: x.get("is_vip", 0), reverse=True)

    return result


# 解析任务数量
def parse_tasks(task_lines: list[str]) -> list[dict]:
    get_today_price()
    tasks = []

    for line in task_lines:
        try:
            phone, pwd, is_vip, task_time,raw_json,token = line.strip().split("-", 5)
            item_dict = eval(raw_json)

            for name, count in item_dict.items():
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

                task = {
                    "name": name,
                    "id": name_id.get(name, ""),
                    "buyCount": count,
                    "maxPrice": name_price.get(name, "99999"),
                    "authorization": token,
                    "phone": phone,
                    "pwd": pwd,
                    "task_time": task_time,
                    "is_vip":is_vip,
                }
                tasks.append(task)

        except Exception as e:
            get_task_log.error(f"解析失败: {line}, 错误: {e}")

    return tasks


