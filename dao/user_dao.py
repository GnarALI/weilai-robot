# dao/user_dao.py
import sqlite3
from dao.db import get_connection
import uuid

class UserDao:

    # 新增用户
    def insert_user(self, wx_name):
        user_id = str(uuid.uuid4())
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO user (id, wx_name) VALUES (?, ?)', (user_id, wx_name))
        conn.commit()
        conn.close()
        return user_id

    # 根据微信名称查询用户
    def get_user_by_wx_name(self, wx_name):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE wx_name = ?', (wx_name,))
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return dict(zip(columns, row)) if row else None

    # 根据手机号查询用户
    def get_user_by_phone(self, phone):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE phone = ?', (phone,))
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return dict(zip(columns, row)) if row else None

    # 根据微信名称更新支付密码
    def update_pay_pwd_by_wx_name(self, wx_name, pay_pwd):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE user SET pay_pwd = ? WHERE wx_name = ?', (pay_pwd, wx_name))
        conn.commit()
        conn.close()

    # 更新 token
    def update_token_by_wx_user(self, wx_name, token, expire_time, phone):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE user SET token = ?, expire_time = ?, phone = ? WHERE wx_name = ?',
                       (token, expire_time, phone, wx_name))
        conn.commit()
        conn.close()

    # 删除用户
    def delete_user_by_phone(self, phone):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user WHERE phone = ?', (phone,))
        conn.commit()
        conn.close()

    # 根据日期获取未执行的任务用户（task_status = 0）
    def get_users_by_task_date(self, date_str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT * FROM user 
            WHERE substr(task_time, 1, 10) = ? AND task_status = 0
            ''',
            (date_str,)
        )
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return [dict(zip(columns, row)) for row in rows]

    # 更新任务状态
    def update_task_status_by_phone(self, phone, status):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE user SET task_status = ? WHERE phone = ?', (status, phone))
        conn.commit()
        conn.close()

    def update_task_status0_by_phone(self, phone):
        self.update_task_status_by_phone(phone, 0)

    def update_task_status1_by_phone(self, phone):
        self.update_task_status_by_phone(phone, 1)

    def update_task_status100_by_phone(self, phone):
        self.update_task_status_by_phone(phone, 100)

    # 按微信昵称更新任务状态为指定值
    def update_task_status_by_wx_name(self, wx_name, status):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE user SET task_status = ? WHERE wx_name = ?', (status, wx_name))
        conn.commit()
        conn.close()

    # 按微信昵称更新任务状态为 0（未开始）
    def update_task_status0_by_wx_name(self, wx_name):
        self.update_task_status_by_wx_name(wx_name, 0)
    def update_task_status1_by_wx_name(self, wx_name):
        self.update_task_status_by_wx_name(wx_name, 1)
    def update_task_status100_by_wx_name(self, wx_name):
        self.update_task_status_by_wx_name(wx_name, 100)

    # 更新成功任务
    def update_success_task_by_phone(self, phone, success_task):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE user SET success_task = ? WHERE phone = ?', (success_task, phone))
        conn.commit()
        conn.close()

    # 设置任务信息
    def update_task_by_wx_name(self, wx_name, task):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE user SET task = ? WHERE wx_name = ?', (task, wx_name))
        conn.commit()
        conn.close()
    #设置任务时间
    def update_task_time_by_wx_name(self, wx_name, task_time):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE user SET task_time = ? WHERE wx_name = ?', (task_time, wx_name))
        conn.commit()
        conn.close()

    # 设置为vip
    def update_is_vip_by_wx_name(self, wx_name):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE user SET is_vip = 1 WHERE wx_name = ?', (wx_name,))
        conn.commit()
        conn.close()
