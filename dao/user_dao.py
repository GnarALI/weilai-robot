# dao/user_dao.py
import sqlite3
from dao.db import get_connection
import uuid

class UserDao:

    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
    # 新增用户
    def insert_user(self, wx_name):
        user_id = str(uuid.uuid4())  # 生成 UUID 并转为字符串
        sql = '''
               INSERT INTO user (id, wx_name)
               VALUES (?,?)
           '''
        self.cursor.execute(sql, (user_id,wx_name))
        self.conn.commit()
        return self.cursor.lastrowid
    # 根据微信名称查询用户
    def get_user_by_wx_name(self, wx_name):
        sql = 'SELECT * FROM user WHERE wx_name = ?'
        self.cursor.execute(sql, (wx_name,))
        row = self.cursor.fetchone()
        if not row:
            return None
        columns = [desc[0] for desc in self.cursor.description]
        return dict(zip(columns, row))

    # 根据手机号查询用户，返回字典
    def get_user_by_phone(self, phone):
        sql = 'SELECT * FROM user WHERE phone = ?'
        self.cursor.execute(sql, (phone,))
        row = self.cursor.fetchone()
        if not row:
            return None
        columns = [desc[0] for desc in self.cursor.description]
        return dict(zip(columns, row))
    # 根据微信名称更新用户支付密码
    def update_pay_pwd_by_wx_name(self, wx_name, pay_pwd):
        sql = 'UPDATE user SET pay_pwd = ? WHERE wx_name = ?'
        self.cursor.execute(sql, (pay_pwd,wx_name ))
        self.conn.commit()
    # 根据微信名称更新用户 token 和过期时间
    def update_token_by_wx_user(self, wx_name, token, expire_time,phone):
        sql = 'UPDATE user SET token = ?, expire_time = ?,phone = ? WHERE wx_name = ?'
        self.cursor.execute(sql, (token, expire_time, phone,wx_name,))
        self.conn.commit()

    def get_user_by_wx_name_dict(self, wx_name):
        sql = 'SELECT * FROM user WHERE wx_name = ?'
        self.cursor.execute(sql, (wx_name,))
        row = self.cursor.fetchone()
        if row:
            columns = [desc[0] for desc in self.cursor.description]
            return dict(zip(columns, row))
        return None

    def delete_user_by_phone(self, phone):
        sql = 'DELETE FROM user WHERE phone = ?'
        self.cursor.execute(sql, (phone,))
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()
    # 根据日期字符串查询用户列表
    def get_users_by_task_date(self, date_str: str) -> list[dict]:
        """
        根据传入日期字符串（格式 yyyy/MM/dd），
        返回所有 task_time 在这一天的用户记录列表（字典形式）
        """
        # 查询时只匹配日期部分，SQLite的substr函数，取前10字符（yyyy/MM/dd）
        sql = """
            SELECT * FROM user
            WHERE substr(task_time, 1, 10) = ?
        """
        self.cursor.execute(sql, (date_str,))
        rows = self.cursor.fetchall()

        users = []
        if rows:
            columns = [desc[0] for desc in self.cursor.description]
            for row in rows:
                users.append(dict(zip(columns, row)))

        return users

    # 根据手机号更新任务状态0未开始
    def update_task_status0_by_phone(self, phone):
        sql = 'UPDATE user SET status = 0 WHERE phone = ?'
        self.cursor.execute(sql, (phone,))
        self.conn.commit()

    # 根据手机号更新任务状态 1进行中
    def update_task_status1_by_phone(self, phone):
        sql = 'UPDATE user SET status = 1 WHERE phone = ?'
        self.cursor.execute(sql, (phone,))
        self.conn.commit()

     # 根据手机号更新任务状态 100已完成
    def update_task_status100_by_phone(self, phone):
        sql = 'UPDATE user SET status = 100 WHERE phone = ?'
        self.cursor.execute(sql, (phone,))
        self.conn.commit()

    # 根据手机号更新成功任务
    def update_success_task_by_phone(self, phone,success_task):
        sql = 'UPDATE user SET success_task = ? WHERE phone = ?'
        self.cursor.execute(sql, (success_task,phone))
        self.conn.commit()

    # 根据微信名称更新用户任务
    def update_task_by_wx_name(self, wx_name, task):
        sql = 'UPDATE user SET task = ? WHERE wx_name = ?'
        self.cursor.execute(sql, (task,wx_name ))
        self.conn.commit()

    # 根据微信名称更新用户任务
    def update_task_time_by_wx_name(self, wx_name, task_time):
        sql = 'UPDATE user SET task_time = ? WHERE wx_name = ?'
        self.cursor.execute(sql, (task_time, wx_name))
        self.conn.commit()





# date_str = "2025/06/26"
# user_list = db.get_users_by_task_date(date_str)
# for user in user_list:
#     print(user['wx_name'], user['task_time'])