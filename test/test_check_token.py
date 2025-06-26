from check_token import check_login_token

if __name__ == "__main__":
    # 替换为你自己的测试手机号和验证码
    phone = "13225269130"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMzM3NTQ2MTczMTIyNjgyODgwIiwiZXhwIjoxNzUxNDMzNTYxfQ.jG4JSHUTWbUwiH7hxm2XKhgdrvk46Q664ULRKEFuWzU"

    results = check_login_token(phone, token)

    if results:
        print(f"✅ 获取成功：{results}")
    else:
        print("❌ 获取失败，请检查验证码或手机号是否正确")