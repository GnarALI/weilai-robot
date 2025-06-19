from login import get_token_by_login

if __name__ == "__main__":
    # 替换为你自己的测试手机号和验证码
    phone = "19170573081"
    sms = "356874"

    token = get_token_by_login(phone, sms)

    if token:
        print(f"✅ 获取成功：{token}")
    else:
        print("❌ 获取失败，请检查验证码或手机号是否正确")