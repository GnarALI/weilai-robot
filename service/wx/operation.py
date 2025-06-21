from accommon.constant import USER_COMMANDS
from service.weilai.login import get_token_by_login
from service.weilai.scheduler import trigger_weilai_task
from dao.user_dao import UserDao
import json
import datetime

user_dao = UserDao()

def get_wx_msg(wx_name, msg):
    msg = msg.strip()

    if msg.startswith("1-"):
        try:
            _, phone, code = msg.split("-")
            token, expires_time = get_token_by_login(phone, code)
            if token:
                try:
                    user_dao.update_token_by_wx_user(wx_name, token, expires_time,phone)
                except Exception as e:
                    print(f"❌ 更新 token 出错: {e}")
                return f"登录成功！\ntoken:{token}\ntoken有效期:{expires_time}"
            else:
                return print(f"❌ 登录失败，请检查输入或重试。{expires_time}")
        except ValueError:
            return f"格式错误！请参考示例：\n{USER_COMMANDS}"
        except Exception as e:
            print(f"❌ 登录流程出错: {e}")
            return "登录失败，请检查输入或重试。"

    elif msg.startswith("2-"):
        try:
            _, pwd = msg.split("-", 1)  # ✅ 只分一次，提取出密码
            try:
                user_dao.update_pay_pwd_by_wx_name(wx_name, pwd)
                return "设置支付密码成功！"
            except Exception as e:
                print(f"❌ 更新支付密码失败：{e}")
                return "设置密码失败，请稍后重试"
        except ValueError:
            return f"格式错误！请参考示例：\n{USER_COMMANDS}"

    elif msg.startswith("3-"):
        try:
            # 1. 拆解消息：分割出时间和 JSON 内容
            _, run_time_str, json_str = msg.split("-", 2)

            # 2. 解析 JSON 内容
            task_dict = json.loads(json_str)

            # 3. 解析时间（支持 yyyy/MM/dd 格式）
            run_time_str = run_time_str.strip('"').strip()
            run_time = datetime.datetime.strptime(run_time_str, "%Y/%m/%d %H:%M:%S")
            run_time_formatted = run_time.strftime("%Y-%m-%d %H:%M:%S")

            # 4. 获取用户信息
            user = user_dao.get_user_by_wx_name_dict(wx_name)
            if not user:
                return f"未找到用户 {wx_name} 的绑定信息"

            phone = user["phone"]
            token = user["token"]
            pay_pwd = user["pay_pwd"]

            # 5. 构造参数
            authorization_list = [f"{phone}:{token}:{pay_pwd}"]
            task_lines = [f"{phone}-{name}-{count}" for name, count in task_dict.items()]


            # 6. 启动抢购任务，传时间字符串（或你自己需要传 datetime）
            trigger_weilai_task(authorization_list, task_lines, run_time_formatted)

            return f"✅ 已为 {phone} 设置抢购任务，将在 {run_time_formatted} 执行"
        except ValueError:
            return f"格式错误！请参考示例：\n{USER_COMMANDS}"

    elif msg.startswith("4-"):
        return "功能暂未开放，敬请期待！"



    else:
        return USER_COMMANDS
