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
    # 可添加多个任务
]

# ✅ 可选：设定定时抢购时间（格式：'2025-06-18 22:30:00'），不需要定时则设为 None
run_time = '2025-06-20 14:58:00'

# ✅ 主函数入口（支持定时）
from service.weilai.scheduler import run_with_schedule

if __name__ == "__main__":
    run_with_schedule(authorization_list, task_lines, run_time)
