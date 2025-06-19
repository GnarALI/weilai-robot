# service/wechat.py

from wxauto import WeChat
import time
import re
from dao.user_dao import UserDao
from accommon.constant import USER_COMMANDS
from service.wx.operation import get_wx_msg

user_dao = UserDao()

class WeChatService:
    def __init__(self, wait=3):
        self.wx = WeChat()
        self.user_list = []
        self.wait = wait
        self.running = False

    def start(self):
        self.running = True
        print("微信监听服务启动...")
        try:
            while self.running:
                try:
                    new_user = self.wx.GetNextNewMessage()
                    if new_user:
                        for raw_key, msg_list in new_user.items():
                            try:
                                clean_key = re.sub(r'\s*\(.*?\)', '', raw_key)
                                is_friend = any(msg[0] != 'SYS' for msg in msg_list)
                                if is_friend and clean_key not in self.user_list:
                                    self.user_list.append(clean_key)
                                    self.wx.AddListenChat(who=clean_key)
                                    print(f'✅ 添加新用户【{clean_key}】到监听列表')

                                    user = user_dao.get_user_by_wx_name(clean_key)
                                    if user is None:
                                        user_dao.insert_user(clean_key)
                                    else:
                                        print(f'👤当前用户数据: {user}')

                                    sender = msg_list[0].sender
                                    print(f'👤 <{sender.center(10, "-")}>：{msg_list[0].content}')

                                    try:
                                        result = get_wx_msg(clean_key, msg_list[0].content)
                                    except Exception as e:
                                        result = f"❌ 指令处理失败: {e}"
                                        print(result)

                                    self.wx.SendMsg(result, clean_key)
                            except Exception as e:
                                print(f'❌ 新用户消息处理失败: {e}')

                    msgs = self.wx.GetListenMessage()
                    for chat, one_msgs in msgs.items():
                        if not one_msgs:
                            continue
                        for msg in one_msgs:
                            try:
                                if msg.type == 'sys':
                                    print(f'📢【系统消息】{msg.content}')
                                elif msg.type == 'friend':
                                    sender = msg.sender
                                    print(f'👤 <{sender.center(10, "-")}>：{msg.content}')
                                    try:
                                        result = get_wx_msg(sender, msg.content)
                                    except Exception as e:
                                        result = f"❌ 指令处理失败: {e}"
                                        print(result)
                                    chat.SendMsg(result)
                                elif msg.type == 'self':
                                    print(f'🗨️ <我自己>：{msg.content}')
                                elif msg.type == 'time':
                                    print(f'⏱️【时间消息】{msg.time}')
                                elif msg.type == 'recall':
                                    print(f'⚠️【撤回消息】{msg.content}')
                            except Exception as e:
                                print(f'❌ 单条消息处理失败: {e}')
                except Exception as loop_err:
                    print(f'❌ 循环内异常: {loop_err}')
                time.sleep(self.wait)
                print(f'当前监听用户列表 : {self.user_list}')
        except KeyboardInterrupt:
            print('👋 微信监听服务停止')
        except Exception as e:
            print(f'❌ 监听主循环异常: {e}')
