from dao.db import init_db
from utils.logger import get_logger
from service.wx.wechat import WeChatService
from service.weilai.scheduler import poll_tasks  # ✅ 导入你刚改名的调度模块
import threading


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

    # 启动调度器线程
    threading.Thread(target=poll_tasks, daemon=True).start()

    # poll_tasks()

    # 启动微信服务监听
    wx_service = WeChatService(wait=3)
    wx_service.start()


if __name__ == '__main__':
    main()
