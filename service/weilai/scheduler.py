# scheduler.py
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from task_service import execute_user_task
from database import get_pending_tasks

# 配置轮询间隔（秒）
POLL_INTERVAL = 10

# 最大线程池大小（全局控制）
MAX_WORKERS = 3000
executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

def schedule_task(task):
    now = datetime.now()
    task_time = task['task_time']
    delay = (task_time - now).total_seconds()

    if delay > 0:
        threading.Timer(delay, executor.submit, args=(execute_user_task, task)).start()
    else:
        executor.submit(execute_user_task, task)

def poll_tasks():
    while True:
        try:
            now = datetime.now()
            # 取出当前时间 ±60s 内，状态为"待执行"的任务
            tasks = get_pending_tasks(within_seconds=60)
            for task in tasks:
                schedule_task(task)
        except Exception as e:
            print(f"[调度异常] {e}")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    print("[调度器] 启动任务轮询...")
    poll_tasks()