# main.py

from dao.db import init_db
from utils.logger import get_logger
from service.wx.wechat import WeChatService


def banner():
    print("""
    ================================
     未来启元抢购工具 - V1.0
     Author: 程宇白 x ChatGPT
    ================================
    """)


def main():
    banner()

    # 初始化日志
    get_logger()

    # 初始化数据库（创建表）
    init_db()

    # 后续扩展：微信监听 / 定时任务 / 抢购模式等入口
    wx_service = WeChatService(wait=3)
    wx_service.start()



if __name__ == '__main__':
    main()