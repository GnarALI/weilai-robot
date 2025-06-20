import sqlite3
import os

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'weilai.db')


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db():
    """初始化数据库建表"""
    conn = get_connection()
    cursor = conn.cursor()

    # 创建 user 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id TEXT PRIMARY KEY,
            wx_name TEXT, 
            phone TEXT, 
            sms_code TEXT, 
            pay_pwd TEXT,   
            token TEXT,   
            expire_time TEXT,
            bind_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status INTEGER DEFAULT 0,
            last_login TIMESTAMP
        )
    ''')


    conn.commit()
    conn.close()
    print("[*] 数据库初始化完成，表已创建")


if __name__ == '__main__':
    init_db()
