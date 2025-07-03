from accommon.constant import USER_COMMANDS, USER_TIP
from service.weilai.login import login
from service.weilai.check_token import check_login_token
from service.weilai.get_price import get_user_task
from dao.user_dao import UserDao
import json
import datetime
from utils.logger import get_logger  # 导入自定义日志工具

# 初始化日志系统
loggers = get_logger()
wx_operation_log = loggers['wx_operation']

# 初始化dao层
user_dao = UserDao()


def get_wx_msg(wx_name, msg):
    msg = msg.strip()

    if msg.startswith("橙心-"):
        try:
            name,phone, u_code, pwd = msg.split("-")
            user=user_dao.get_user_by_phone(phone)
            if user is None:
                user_dao.insert_user(wx_name, phone,pwd)
                token, expires_time = login(phone, u_code)
                if token is None:
                    return "验证码错误"
                user_dao.update_token_by_phone(phone, token, expires_time)
                code, balance = check_login_token(phone, token)
                if code==100:
                    user_dao.update_balance_by_phone(phone,balance)
                else:
                    return "请重试"

            else:
                user_dao.update_pwd_by_phone(phone,pwd)
                code,balance=check_login_token(phone,user["token"])
                if code==100:
                    user_dao.update_balance_by_phone(phone,balance)

                else:
                    token, expires_time = login(phone, u_code)
                    if token:
                        user_dao.update_token_by_phone(phone, token, expires_time)
                    else:
                        return "登录状态已失效，请重新发送验证码"

            task=get_user_task(phone)

            return task

        except Exception as e:
            weilai_log = f"设置优先用户失败，错误原因: {e}\n请稍后重试或联系管理员。"
            return weilai_log

    elif msg.startswith("橙心vip-"):
        phone = msg.split("-")
        try:
            user_dao.update_is_vip_by_phone(phone)
            return "设为优先用户成功！"
        except Exception as e:
            # 捕获所有异常，打印日志或详细错误
            vip_log = f"设置优先用户失败，错误原因: {e}\n请稍后重试或联系管理员。"
            wx_operation_log.error(vip_log)
            return vip_log

    else:
        return USER_TIP
