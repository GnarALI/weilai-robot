from accommon.constant import USER_COMMANDS,USER_TIP
from service.weilai.login import get_token_by_login
from service.weilai.check_token import check_login_token
from dao.user_dao import UserDao
import json
import datetime
from utils.logger import get_logger  # 导入自定义日志工具
# 初始化日志系统
loggers = get_logger()
wx_operation_log = loggers['wx_operation']

#初始化dao层
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
                    login_log=f"❌ 更新 token 出错: {e}"
                    wx_operation_log.error(login_log)

                login_log=f"登录成功！\ntoken:{token}\ntoken有效期:{expires_time}"
                wx_operation_log.info(login_log)
                return f"预计登录有效期至:{expires_time}"
            else:
                login_log=f"❌ 登录失败，请检查输入或重试。{expires_time}"
                wx_operation_log.error(expires_time)
                return login_log
        except ValueError:
            return f"格式错误！请参考示例：\n{USER_TIP}"
        except Exception as e:
            login_log = f"❌ 登录流程出错: {e}"
            wx_operation_log.error(login_log)
            return "登录失败，请检查输入或重试。"

    elif msg.startswith("2-"):
        try:
            _, pay_pwd = msg.split("-", 1)  # ✅ 只分一次，提取出密码
            try:
                user_dao.update_pay_pwd_by_wx_name(wx_name, pay_pwd)
                return "设置支付密码成功！"
            except Exception as e:
                pwd_log = f"❌ 登录流程出错: {e}"
                wx_operation_log.error(pwd_log)
                return "设置密码失败，请稍后重试"
        except ValueError:
            return f"格式错误！请参考示例：\n{USER_TIP}"

    elif msg.startswith("3-"):
        try:
            # 1. 拆分消息，拿到对应的任务数据存到sqllite3中
            _, task = msg.split("-", 1)
            try:
                user_dao.update_task_by_wx_name(wx_name,task)
                return "设置抢购任务成功！"
            except Exception as e:
                task_log = f"❌ 设置抢购任务失败: {e}"
                wx_operation_log.error(task_log)
                return "设置抢购任务失败,请稍后重试"
        except ValueError:
            return f"格式错误！请参考示例：\n{USER_TIP}"

    elif msg.startswith("4-"):
        try:
            # 1. 拆分消息，拿到对应的任务数据存到sqllite3中
            _, task_time = msg.split("-", 1)
            try:
                user = user_dao.get_user_by_wx_name(wx_name)
                result=check_login_token(user["phone"], user["token"])

                if result!=100:
                    token_status = f"用户:{wx_name} 手机号:{user['phone']} 登录状态已失效，请重新登录"
                    wx_operation_log.warning(token_status)
                    return token_status


                user_dao.update_task_time_by_wx_name(wx_name, task_time)
                user_dao.update_task_status0_by_wx_name(wx_name)

                return "设置抢购任务时间成功！"
            except Exception as e:
                task_time_log = f"❌ 设置抢购任务时间失败: {e}"
                wx_operation_log.error(task_time_log)
                return "设置抢购时间任务失败,请稍后重试"
        except ValueError:
            return f"格式错误！请参考示例：\n{USER_TIP}"

    elif msg.startswith("5"):
        try:
            try:
                user = user_dao.get_user_by_wx_name(wx_name)
                success_task = ""  # 先给个默认空字符串
                if user and user.get("success_task"):
                    success_task = user.get("success_task")
                else:
                    success_task = "暂无记录"  # 或你想返回的默认提示
                return success_task
            except Exception as e:
                task_log = f"❌ 获取成功任务失败: {e}"
                wx_operation_log.error(task_log)
                return "获取成功任务失败，请稍后重试"
        except ValueError:
            return f"格式错误！请参考示例：\n{USER_TIP}"

    elif msg.startswith("6"):
        try:
            return USER_TIP
        except ValueError:
            return f"格式错误！请参考示例：\n{USER_TIP}"

    elif msg.startswith("you酸萝卜别吃"):
        try:
            user_dao.update_is_vip_by_wx_name(wx_name)
            return "设为优先用户成功！"
        except Exception as e:
            # 捕获所有异常，打印日志或详细错误
            vip_log=f"设置优先用户失败，错误原因: {e}\n请稍后重试或联系管理员。"
            wx_operation_log.error(vip_log)
            return vip_log

    else:
        return USER_COMMANDS
