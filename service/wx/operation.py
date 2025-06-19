from accommon.constant import USER_COMMANDS
from service.weilai.login import get_token_by_login
from dao.user_dao import UserDao

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
        return "还没写好急个几鸡巴"

    elif msg.startswith("3-"):
        return "还没写好急个几鸡巴"

    elif msg.startswith("4-"):
        try:
            _, pwd = msg.split("-")
            try:
                user_dao.update_pay_pwd_by_wx_name(wx_name, pwd)
                return "设置支付密码成功！"
            except Exception as e:
                print(f"❌ 更新支付密码失败：{e}")
                return "设置密码失败，请稍后重试"
        except ValueError:
            return f"格式错误！请参考示例：\n{USER_COMMANDS}"
    elif msg=="5":
            return "怎么还有酸萝卜♂别吃的皇子不用上课，妈的！"



    else:
        return USER_COMMANDS
