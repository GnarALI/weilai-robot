import datetime
from service.weilai.task import start_task

# ✅ 设置抢购参数：
authorization_list = [
    # 格式：手机号:token:支付密码
    "13225269130:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMzM3NTQ2MTczMTIyNjgyODgwIiwiZXhwIjoxNzUxMDA3MTAxfQ.o0gGygtuJQT5SW7vXBCYQcx73GWgHUn0JLZ8w4drtxc:123123",
    # 可添加多个用户
]

task_lines = [
    # 格式：手机号-商品名称-数量
    "13225269130-探索未来-3",
    "13225269130-法老-3",
    "13225269130-金宝-3",
    "13225269130-炎宝-3",
    "13225269130-水宝-3",
    "13225269130-双鱼瑟琳-3",
    "13225269130-水瓶西尔-3",
    "13225269130-金牛维塔-3",
    "13225269130-羊白诺亚-3",
    # 可添加多个任务
]

# ✅ 可选：设定定时抢购时间（格式：'2025-06-18 22:30:00'），不需要定时则设为 None
run_time = '2025-06-22 13:52:00'

# ✅ 主函数入口（支持定时）
from service.weilai.scheduler import run_with_schedule

if __name__ == "__main__":
    run_with_schedule(authorization_list, task_lines, run_time)
