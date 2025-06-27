# scheduler.py
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from service.weilai.get_task import get_today_task_detail
from dao import user_dao

user_dao=user_dao.UserDao

# 配置轮询间隔（秒）
POLL_INTERVAL = 10

# 最大线程池大小（全局控制）
MAX_WORKERS = 1000
executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

# 时间窗口：±30分钟（秒）
TIME_WINDOW_SECONDS = 30 * 60


def schedule_task(task: dict, repeat_count: int = 1):
    from service.weilai.task import send_request  # ✅ 延迟导入，打破循环引用
    """
    安排任务执行，可设置重复次数（例如VIP用户多线程并发）
    """
    now = datetime.now()
    task_time = task['task_time']
    delay = (task_time - now).total_seconds()

    def run_task():
        print(f"[调度任务] {task['phone']} | VIP: {task.get('is_vip')} | 线程数: {repeat_count}")
        for _ in range(repeat_count):
            executor.submit(send_request, task)

        # 更新任务状态为已执行
        try:
            user_dao.update_task_status1_by_phone(task['phone'])
        except Exception as e:
            print(f"[更新状态失败] {task['phone']} 错误: {e}")

    if delay > 0:
        print(f"[等待执行] {task['phone']} 将在 {delay:.2f} 秒后执行")
        threading.Timer(delay, run_task).start()
    else:
        print(f"[立即执行] {task['phone']}")
        run_task()


def poll_tasks():
    """
    循环轮询数据库并调度任务执行
    """
    while True:
        try:
            now = datetime.now()
            tasks = get_today_task_detail()  # list[dict]

            for task in tasks:
                # 转换时间字段
                task_time = datetime.strptime(task['task_time'], "%Y/%m/%d %H:%M:%S")
                task['task_time'] = task_time

                # 校验是否在±30分钟范围内
                time_diff = abs((task_time - now).total_seconds())
                if time_diff > TIME_WINDOW_SECONDS:
                    print(f"[跳过任务] 超出时间范围: {task['phone']} 任务时间: {task_time}")
                    continue

                # 判断VIP等级，分配线程数量
                is_vip = task.get("is_vip", 0)
                repeat_count = 3 if is_vip else 1

                schedule_task(task, repeat_count=repeat_count)

        except Exception as e:
            print(f"[调度异常] {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    print("[调度器] 启动任务轮询...")
    poll_tasks()
