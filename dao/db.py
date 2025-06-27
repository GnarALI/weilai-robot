import sqlite3
import os

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'weilai.db')


def get_connection():

    """获取数据库连接，允许跨线程"""
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    """初始化数据库建表"""
    conn = get_connection()
    cursor = conn.cursor()

    # 创建 user 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id TEXT PRIMARY KEY,           -- 用户唯一标识（比如 UUID）
            wx_name TEXT,                  -- 微信昵称
            phone TEXT UNIQUE,             -- 手机号
            pay_pwd TEXT,                  -- 支付密码
            token TEXT,                    -- 登录 token
            expire_time TEXT,              -- token 过期时间
            task TEXT,                     -- 抢购任务 JSON 字符串
            task_time TEXT,                -- 任务执行时间（格式: yyyy/MM/dd HH:mm:ss）
            task_status INTEGER DEFAULT 0, -- 任务状态（如: 0 未开始，1 进行中，100 已完成）
            is_vip INTEGER DEFAULT 0,       -- 是否是VIP用户（1 是，0 否）
            success_task TEXT             -- 成功的任务 JSON 字符串
        )
    ''')

    conn.commit()
    conn.close()
    print("[*] 数据库初始化完成，表已创建")

if __name__ == '__main__':
    init_db()
