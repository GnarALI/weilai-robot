from wxauto import WeChat
import time
import hashlib
from dao.user_dao import UserDao
from service.wx.operation import get_wx_msg
from utils.logger import get_logger

loggers = get_logger()
wx_chat_log = loggers['wx_chat']
user_dao = UserDao()


class WeChatService:

    def __init__(self, wait=3):
        self.wx = WeChat()
        self.user_list = []
        self.wait = wait
        self.running = False
        self.last_msg_record = {}  # ✅ 添加：记录用户最近的消息摘要

    def _get_msg_hash(self, msg_list):
        """
        将消息列表中提取的文本内容拼接后生成哈希值用于去重
        """
        text_list = []
        for msg in msg_list:
            try:
                text_list.append(str(msg.content))  # 提取消息文本内容
            except Exception as e:
                wx_chat_log.warning(f"⚠️ 无法解析消息内容: {e}")
                text_list.append("")

        joined = '|'.join(text_list)
        return hashlib.md5(joined.encode('utf-8')).hexdigest()

    def start(self):
        self.running = True
        wx_chat_log.info("✅ 微信监听服务启动...")
        try:
            while self.running:
                try:
                    new_user = self.wx.GetNextNewMessage()
                    if new_user:
                        for raw_key, msg_list in new_user.items():
                            msg_hash = self._get_msg_hash(msg_list)
                            last_hash = self.last_msg_record.get(raw_key)

                            # ✅ 判断是否为重复消息
                            if last_hash == msg_hash:
                                wx_chat_log.debug(f"🔁 忽略重复消息，来自: {raw_key}")
                                continue  # 跳过本次

                            # ✅ 保存新的 hash
                            self.last_msg_record[raw_key] = msg_hash

                            try:
                                wx_chat_log.info(f"📨 收到新消息，来自 {raw_key}: {msg_list}")
                                for item in msg_list:
                                    if item.type !='friend':
                                        continue
                                    results = get_wx_msg(item.sender,item.content)
                                    if results:
                                        self.wx.SendMsg(results, raw_key)
                            except Exception as e:
                                wx_chat_log.error(f'❌ 新用户消息处理失败: {e}')
                    time.sleep(self.wait)
                except Exception as e:
                    wx_chat_log.error(f'❌ 单次监听异常: {e}')
        except KeyboardInterrupt:
            wx_chat_log.warning('👋 微信监听服务手动停止')
        except Exception as e:
            wx_chat_log.error(f'❌ 监听主循环异常: {e}')
