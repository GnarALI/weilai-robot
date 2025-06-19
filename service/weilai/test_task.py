import datetime
from service.weilai.task import start_task

# ✅ 设置抢购参数：
authorization_list = [
    # 格式：手机号:token:支付密码
    "19912345678:你的token字符串:支付密码",
    # 可添加多个用户
]

task_lines = [
    # 格式：手机号-商品名称-数量
    "19912345678-蛇来运转-1",
    # 可添加多个任务
]

# ✅ 可选：设定定时抢购时间（格式：'2025-06-18 22:30:00'），不需要定时则设为 None
run_time = None

# ✅ 主函数入口（支持定时）
from service.weilai.scheduler import run_with_schedule

if __name__ == "__main__":
    run_with_schedule(authorization_list, task_lines, run_time)
