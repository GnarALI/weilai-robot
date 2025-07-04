from service.wx.operation import get_wx_msg

if __name__ == "__main__":
    # 替换为你自己的测试手机号和验证码
    msg = "橙心-19170573081-024455-649735"

# 360311200110244553
    results= get_wx_msg("随便", msg)

    if results:
        print(f"✅ 获取成功：{results}")
    else:
        print("❌ 获取失败，请检查验证码或手机号是否正确")

