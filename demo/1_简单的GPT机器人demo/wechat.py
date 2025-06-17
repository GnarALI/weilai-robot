from wxauto import WeChat
import time
import re

wx = WeChat()
user_list = []
wait = 3  # 每3秒检查一次新消息

try:
    while True:
        new_user = wx.GetNextNewMessage()

        if new_user:
            # 遍历所有键值对（聊天对象: 消息列表）
            for raw_key, msg_list in new_user.items():
                clean_key = re.sub(r'\s*\(.*?\)', '', raw_key)
                is_friend = any(msg[0] != 'SYS' for msg in msg_list)

                if is_friend and clean_key not in user_list:
                    user_list.append(clean_key)
                    wx.AddListenChat(who=clean_key)
                    print(f'✅ 添加新用户【{clean_key}】到监听列表')
                    sender = msg_list[0].sender
                    print(f'👤 <{sender.center(10, "-")}>：{msg_list[0].content}')
                    wx.SendMsg("收到", clean_key)



        # 获取监听中的消息
        msgs = wx.GetListenMessage()
        for chat in msgs:
            one_msgs = msgs.get(chat)
            if not one_msgs:
                continue

            for msg in one_msgs:
                if msg.type == 'sys':
                    print(f'📢【系统消息】{msg.content}')

                elif msg.type == 'friend':
                    sender = msg.sender
                    print(f'👤 <{sender.center(10, "-")}>：{msg.content}')
                    chat.SendMsg('收到')  # 自动回复

                elif msg.type == 'self':
                    print(f'🗨️ <我自己>：{msg.content}')

                elif msg.type == 'time':
                    print(f'⏱️【时间消息】{msg.time}')

                elif msg.type == 'recall':
                    print(f'⚠️【撤回消息】{msg.content}')

        time.sleep(wait)
        print(f'当前监听用户列表 : {user_list}')

except KeyboardInterrupt:
    print('👋 程序退出，Bye~')
except Exception as e:
    print(f'❌ 发生错误: {e}')
