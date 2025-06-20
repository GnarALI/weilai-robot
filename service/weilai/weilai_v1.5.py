import optparse
import time
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import threading
import datetime
import logging
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('weilai.log'),
        logging.StreamHandler()
    ]
)

# 配置成功日志记录器
success_logger = logging.getLogger('success_logger')
success_logger.setLevel(logging.INFO)
success_handler = logging.FileHandler('success.log')
success_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
success_handler.setFormatter(success_formatter)
success_logger.addHandler(success_handler)

# 接口地址
url = "https://www.weilaiqiyuan.com/core/buyout_products/buy/order/bulk"

# authorization = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjU0MDQ1Njc1NzQ1Mjc2NCIsImV4cCI6MTc0MzE1MzAwNH0.Av6nKri_fuJGn3TkULnzFcq2ehyPwVbEKyogvaNNLY0"
# 要发送的 JSON 数据
# data = {
#     "name":"蛇来运转",
#     "id":"100",
#     "buyCount":3,
#     "maxPrice":"14933.99",
#     "authorization":authorization
# }



# 请求头
headers = {
    "Content-Type": "application/json",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
    "Authorization":"",
    "version":"1540",
    "deviceType":"ios",
    "imei":"112223223",
    "inner":"112223223",
    "Origin":"https://www.weilaiqiyuan.com"
}

# 循环次数
loop_count = 9999999
# 线程数量
thread_count = 10

name_id = {}
phone_authorization = {}
phone_password = {}
name_price = {}


error_codes = ['500','989897']
# error_codes = []

def generate_random_ipv4():
    octets = [random.randint(0, 255) for _ in range(4)]
    return '.'.join(map(str, octets))

def send_request(data):
    data_send = {
        "name": data['name'],
        "id": data['id'],
        "buyCount": data['buyCount'],
        "maxPrice": data['maxPrice'],
        "authorization": data['authorization']
    }

    # logging.info(data)
    request_header1 = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
        "Authorization": data['authorization'],
        "version": "1540",
        "deviceType": "ios",
        "imei": "112223223",
        "inner": "112223223",
        "Origin": "https://www.weilaiqiyuan.com"
    }

    # logging.info(str(request_header)+"-"+data['phone'])

    for _ in range(loop_count):
        try:
            fake_ip = generate_random_ipv4()
            request_header1 = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
                "Authorization": data['authorization'],
                "Version": "1540",
                "X-Token": data['authorization'],
                "DeviceId": "204cd84eee62335d1b5821d6b478c589d",
                "Imei": "204cd84eee62335d1b5821d6b478c589d",
                "deviceType": "android",
                "Login_type": "wlld",
                "Referer": "https://api-sc.weilaiqiyuan.com/core/buyout_products/buy/order/bulk",
                "SDKVersionName": "9",
                "DeviceSysVersion": "9",
                "AppVersionCode": "1126",
                "ChannelName": "wlqy",
                "imei": "112223223",
                "inner": "112223223",
                "Origin": "https://www.weilaiqiyuan.com",
                "X-Forwarded-For": fake_ip,
                "CLIENT_IP": fake_ip,
                "REMOTE_ADDR": fake_ip,
                "Via": fake_ip,
                "Connection": "close"
            }
            response = requests.post(url, json=data_send, headers=request_header1,timeout=30)
            # print(response.text)
            if response.status_code != 200:
                if response.status_code != 503:
                    logging.error(f"[{data['phone']}]{data['name']}请求出错：响应码{response.status_code}, 响应内容：{response.text}")
                continue
            # response.raise_for_status()
            # 解析响应为 JSON 格式
            response_json = response.json()
            if response_json.get('code') == '10' or response_json.get('code') == '0' or response_json.get('code') == '500':
                continue
            # print(response_json)
            # print(f"请求成功，状态码: {response.status_code}, 响应内容: {response_json}")
            # 这里可以添加对响应 JSON 数据的处理逻辑
            ### {"timestamp":"2025-04-08T12:15:30.144+0000","status":500,"error":"Internal Server Error","message":"token过期","path":"/core/buyout_products/buy/order/bulk"}

            process_response(data,response_json,request_header1)
        except requests.exceptions.RequestException as e:
            logging.error(f"[!][{data['phone']}]请求出错: {e}")
        except ValueError as e:
            logging.error(f"[!][{data['phone']}]响应内容不是有效的 JSON 格式: {e}")
        except Exception as e:
            logging.error(f"[!][{data['phone']}]未知错误: {e}")

def order(data,orderNo,request_header1):
    data_order = {
        "authorization": data['authorization'],
        "id": orderNo,
        "isBalanceDiscount": 1,
        "payType": 7,
        "pwd": data['pwd']
    }

    retries = 0
    while retries < 20:
        try:
            response = requests.post("https://www.weilaiqiyuan.com/core/buyout_products/pay/order", json=data_order,headers=request_header1,timeout=3)
            # 解析响应为 JSON 格式
            response_json = response.json()
            # print(response_json)
            if response_json['code'] == "200":
                success_logger.info(f"[*][{data['phone']}]{data['name']}支付成功, 订单号: {orderNo}")
            else:
                success_logger.info(f"[-][{data['phone']}]{data['name']}支付失败, 订单号: {orderNo}, 响应内容: {response_json}")
            break
        except requests.exceptions.RequestException as e:
            success_logger.error(f"[!][{data['phone']}]{data['name']} 订单号{orderNo}支付请求出错: {e}")
            retries += 1
        except ValueError as e:
            success_logger.error(f"[!][{data['phone']}]{data['name']} 订单号{orderNo}支付请求出错: 响应内容不是有效的 JSON 格式: {e}")
            retries += 1
        except Exception as e:
            success_logger.error(f"[!][{data['phone']}]{data['name']}支付请求未知错误: {e}")



def process_response(data,response_json,request_header1):
    # if response_json.get('status','') != '':
    #     logging.error(f"[{data['phone']}]{data['name']}请求失败，响应内容{response_json}")
    #     return
    if response_json['code'] == '200':
        success_logger.info(
            f"[+][{data['phone']}]{data['name']}锁单成功，数量: {len(response_json['data']['childOrders'])}, 订单号: {response_json['data']['orderNo']}")
        order(data, response_json['data']['orderNo'], request_header1)
    # logging.info(f"[+][{data['phone']}]{data['name']}请求成功，状态码: {response_json['code']}, 响应内容: {response_json}")
    # if response_json['code'] not in error_codes:
    #     # if name == "蛇来运转":
    #     if response_json['code'] == '200':
    #         success_logger.info(f"[+][{data['phone']}]{data['name']}锁单成功，数量: {len(response_json['data']['childOrders'])}, 订单号: {response_json['data']['orderNo']}")
    #         order(data,response_json['data']['orderNo'],request_header1)
    #     logging.info(f"[+][{data['phone']}]{data['name']}请求成功，状态码: {response_json['code']}, 响应内容: {response_json}")
    if response_json['code'] != '989897':
        logging.info(f"[*]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{data['phone']}]{data['name']}请求成功，状态码: {response_json['code']}, 响应内容: {response_json}")
    # print(f"[*]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{data['phone']}]{data['name']}请求成功，状态码: {response_json['code']}, 响应内容: {response_json}")

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
            # price_list.append({
            #     "name": i['collectionDetailRes']['name'],
            #     "id": i['collectionDetailRes']['id'],
            #     "maxPrice": i['collectionDetailRes']['currentDayMaxPrice'],
            # })
            # data_e = {
            #     "name": i['collectionDetailRes']['name'],
            #     "id": i['collectionDetailRes']['id'],
            #     "buyCount":3,
            #     "maxPrice": i['collectionDetailRes']['currentDayMaxPrice'],
            #     "authorization": authorization
            # }
            # print(data_e)
            # data_list.append(data_e)
        # print(f"请求成功，状态码: {response.status_code}, 响应内容: {response_json}")
        # 这里可以添加对响应 JSON 数据的处理逻辑
    except requests.exceptions.RequestException as e:
        logging.error(f"请求出错: {e}")
        time.sleep(3)
        get_today_price()
    except ValueError as e:
        logging.error(f"响应内容不是有效的 JSON 格式: {e}")
        time.sleep(3)
        get_today_price()
    # logging.info(name_price)


def get_token_by_login(phone,sms):

    login_data = {
        "loginName":phone,
        "smsCode":sms
    }
    try:
        response = requests.post("https://www.weilaiqiyuan.com/core/cuser/public/login", json=login_data, headers=headers,timeout=3)
        response.raise_for_status()
        # 解析响应为 JSON 格式
        response_json = response.json()
        if response_json['code'] != '200':
            print(f"[!]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{phone}]登陆失败！")
            logging.error(f"{response_json}")
            return ""
        token = response_json['data']['token']
        return token
    except requests.exceptions.RequestException as e:
        logging.error(f"请求出错: {e}")
        time.sleep(3)
        return get_token_by_login(phone,sms)

    except ValueError as e:
        logging.error(f"响应内容不是有效的 JSON 格式: {e}")
        time.sleep(3)
        return get_token_by_login(phone,sms)



def generateTask(data_list):
    task_list = []
    for data in data_list:
        task_data = data.split("-")
        authorization = phone_authorization.get(task_data[0])
        if authorization is not None:
            if task_data[1] == '蛇来运转':
                task_data[1] = '蛇来运转-Ⅰ代'
            elif task_data[1] == '魔礼青':
                task_data[1] = '四大天王-魔礼青'
            elif task_data[1] == '魔礼海':
                task_data[1] = '四大天王-魔礼海'
            data_e = {
                "name": task_data[1],
                "id": name_id[task_data[1]],
                "buyCount": task_data[2],
                "maxPrice": name_price[task_data[1]],
                "authorization": authorization,
                "phone":task_data[0],
                "pwd": phone_password.get(task_data[0],'')
            }
            task_list.append(data_e)


    return task_list

def run(authorizations):
    for authorization in authorizations:
        tempdata = authorization.split(":")
        phone_authorization[tempdata[0]] = tempdata[1]
        phone_password[tempdata[0]] = tempdata[2]

    get_today_price()

    data_list = read_txt_file("task.txt")

    task_list = generateTask(data_list)
    # logging.info(task_list)
    logging.info(f"共{len(task_list)}条任务")
    logging.info(f"线程共{len(task_list)*thread_count}个")
    time.sleep(3)
    # 创建并启动线程
    threads = []
    for i in task_list:
        for _ in range(thread_count):
            thread = threading.Thread(target=send_request, args=(i,))
            threads.append(thread)
            thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    logging.info("[*]所有请求已完成。")


def write_to_file(file_path, content):
    """将字符串写入文本文件"""
    with open(file_path, 'a') as file:
        file.write(content)

def read_from_file(file_path):
    """从文本文件中读取字符串"""
    with open(file_path, 'r') as file:
        return file.read()

def read_txt_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            # 去除每行末尾的换行符
            lines = [line.strip() for line in lines]
            return lines
    except FileNotFoundError:
        print(f"错误：未找到文件 {file_path}。")
    except Exception as e:
        print(f"发生未知错误：{e}。")

# def test_token_valild(authorization):
#     data = {
#         "name": "天翼星穹",
#         "id": "96",
#         "buyCount": 3,
#         "maxPrice": "4221.86",
#         "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjU0MDQ1Njc1NzQ1Mjc2NCIsImV4cCI6MTc0MzIyMzkwMn0.QsDpSD0rwmQPDFCM_ztBxCp3CL-j3JETEvhLAdchV14"}
#     try:
#         response = requests.post(url, json=data, headers=headers)
#         response.raise_for_status()
#         # 解析响应为 JSON 格式
#         response_json = response.json()
#         # print(response_json)
#         # print(f"请求成功，状态码: {response.status_code}, 响应内容: {response_json}")
#         # 这里可以添加对响应 JSON 数据的处理逻辑
#         process_response(data['name'], response_json)
#     except requests.exceptions.RequestException as e:
#         logging.error(f"请求出错: {e}")
#     except ValueError as e:
#         logging.error(f"响应内容不是有效的 JSON 格式: {e}")
def get_show_banner():
    print("""
////////////////////////////////////////////////////////////////////
//                          _ooOoo_                               //
//                         o8888888o                              //
//                         88" . "88                              //
//                         (| ^_^ |)                              //
//                         O\  =  /O                              //
//                      ____/`---'\____                           //
//                    .'  \\\\|     |//  `.                         //
//                   /  \\\\|||  :  |||//  \                        //
//                  /  _||||| -:- |||||-  \                       //
//                  |   | \\\\\  -  /// |   |                       //
//                  | \_|  ''\---/''  |   |                       //
//                  \  .-\__  `-`  ___/-. /                       //
//                ___`. .'  /--.--\  `. . ___                     //
//              ."" '<  `.___\_<|>_/___.'  >'"".                  //
//            | | :  `- \`.;`\ _ /`;.`/ - ` : | |                 //
//            \  \ `-.   \_ __\ /__ _/   .-` /  /                 //
//      ========`-.____`-.___\_____/___.-`____.-'========         //
//                           `=---='                              //
//      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^        //
//            佛祖保佑       子弹打空     永不空军                //
////////////////////////////////////////////////////////////////////

Name: 未来启元捡漏小工具
Author : Dean
Version: V1.5""")
    print("==========================完美的分割线===================================")


if __name__ == '__main__':
    get_show_banner()
    parser = optparse.OptionParser('python3 weilai.py -m login -x 15395935018-666666-666666')
    parser.add_option('-x', dest='loginString', type='string', help='手机号-短信验证码-支付密码')
    parser.add_option('-m', dest='mode', type='string', help='login or go')
    parser.add_option('-t', dest='thread', type='int', default=10, help='单条任务线程数')
    parser.add_option('-r', dest='run_time', type='string', help='开始运行时间')

    (options, args) = parser.parse_args()  # 读取用户输入参数

    if options.mode == "login":
        x = options.loginString.split('-')
        phone = x[0]
        smsCode = x[1]
        pwd = x[2]
        token = get_token_by_login(phone,smsCode)
        if token != "":
            print(f"[*]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{phone}]登陆成功!\n{token}")
            write_to_file("token.txt",f"{phone}:{token}:{pwd}\n")

    elif options.mode == "go":
        thread_count = options.thread
        # test_token_valild()
        authorizations = read_txt_file("token.txt")
        if len(authorizations) == 0:
            print("没有登陆的账号")
        else:
            if options.run_time:
                scheduler = BlockingScheduler()
                now = datetime.datetime.now()
                try:
                    target_time_str = f"{now.date()} {options.run_time}"
                    target_time = datetime.datetime.strptime(target_time_str, "%Y-%m-%d %H:%M:%S")
                    print(target_time)
                    if target_time < now:
                        target_time = target_time + datetime.timedelta(days=1)
                except ValueError:
                    print("时间格式错误，请使用 HH:MM:SS 格式。")
                    exit(1)
                scheduler.add_job(run, 'date', run_date=target_time,args=[authorizations])
                try:
                    print(f"任务将在 {target_time} 执行。")
                    scheduler.start()
                except (KeyboardInterrupt, SystemExit):
                    scheduler.shutdown()
            else:
                run(authorizations)
