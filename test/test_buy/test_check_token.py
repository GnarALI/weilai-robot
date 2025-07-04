from service.weilai.buy.check_token import check_login_token

if __name__ == "__main__":
    # 替换为你自己的测试手机号和验证码
    phone = "19170573081"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMzc4NzMzODc4ODgzOTk2NzY4IiwiZXhwIjoxNzUyMDIzOTc4fQ.pM3GeT1krP_H6Qb0_QqiKs6rs188Rn8MekdMnrCjRjs"

    results,balance = check_login_token(phone, token)

    if results:
        print(f"✅ 获取成功：{results,balance}")
    else:
        print("❌ 获取失败，请检查验证码或手机号是否正确")