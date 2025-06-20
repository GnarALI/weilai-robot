# dao/user_dao.py
import sqlite3
from dao.db import get_connection

class UserDao:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def insert_user(self, wx_name):
        sql = '''
               INSERT INTO user (wx_name)
               VALUES (?)
           '''
        self.cursor.execute(sql, (wx_name,))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_user_by_wx_name(self, wx_name):
        sql = 'SELECT * FROM user WHERE wx_name = ?'
        self.cursor.execute(sql, (wx_name,))
        return self.cursor.fetchone()

    def get_user_by_phone(self, phone):
        sql = 'SELECT * FROM user WHERE phone = ?'
        self.cursor.execute(sql, (phone,))
        return self.cursor.fetchone()

    def update_pay_pwd_by_wx_name(self, wx_name, pay_pwd):
        sql = 'UPDATE user SET pay_pwd = ? WHERE wx_name = ?'
        self.cursor.execute(sql, (pay_pwd,wx_name ))
        self.conn.commit()

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
