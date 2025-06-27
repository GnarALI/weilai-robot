# enhanced_scheduler.py
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from service.weilai.get_task import get_today_task_detail
from dao.user_dao import UserDao
from utils.logger import get_logger
import subprocess
import psutil

user_dao = UserDao()
loggers = get_logger()
scheduler_log = loggers['scheduler']

POLL_INTERVAL = 10
MAX_WORKERS = 1000
executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
TIME_WINDOW_SECONDS = 30 * 60

def monitor_resources():
    try:
        output = subprocess.check_output("netstat -n", shell=True, text=True)
        lines = output.splitlines()

        total = 0
        time_wait = 0
        established = 0
        for line in lines:
            if "TCP" in line:
                total += 1
                if "TIME_WAIT" in line:
                    time_wait += 1
                elif "ESTABLISHED" in line:
                    established += 1

        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory().percent

        scheduler_log.info(f"[端口监控] 总连接数: {total} | ESTABLISHED（已建立连接）: {established} | TIME_WAIT（等待关闭连接）: {time_wait}")

        scheduler_log.info(f"[资源使用] CPU使用率: {cpu}% | 内存使用率: {mem}%")
    except Exception as e:
        scheduler_log.error(f"[资源监控异常] {e}")

def schedule_task(task: dict, repeat_count: int = 1):
    from service.weilai.task import send_request  # 延迟导入
    now = datetime.now()
    task_time = task['task_time']
    delay = (task_time - now).total_seconds()

    def run_task():
        scheduler_log.info(f"[调度任务] {task['phone']} | VIP: {task.get('is_vip')} | 线程数: {repeat_count}")
        for _ in range(repeat_count):
            executor.submit(send_request, task)

        try:
            user_dao.update_task_status1_by_phone(task['phone'])
        except Exception as e:
            scheduler_log.error(f"[更新状态失败] {task['phone']} 错误: {e}")

    if delay > 0:
        scheduler_log.info(f"[等待执行] {task['phone']} 将在 {delay:.2f} 秒后执行")
        threading.Timer(delay, run_task).start()
    else:
        scheduler_log.info(f"[立即执行] {task['phone']}")
        run_task()

def poll_tasks():
    scheduler_log.info("[调度器] 启动任务轮询...")
    while True:
        try:
            now = datetime.now()
            tasks = get_today_task_detail()

            for task in tasks:
                task_time = datetime.strptime(task['task_time'], "%Y/%m/%d %H:%M:%S")
                task['task_time'] = task_time
                time_diff = abs((task_time - now).total_seconds())
                if time_diff > TIME_WINDOW_SECONDS:
                    scheduler_log.warning(f"[跳过任务] 超出时间范围: {task['phone']} 任务时间: {task_time}")
                    continue

                is_vip = int(task.get("is_vip", 0))
                repeat_count = 3 if is_vip == 1 else 1

                schedule_task(task, repeat_count=repeat_count)

        except Exception as e:
            scheduler_log.error(f"[调度异常] {e}")

        monitor_resources()
        scheduler_log.info(f"[线程池] 活跃线程数: {threading.active_count()} | 最大线程池: {MAX_WORKERS}")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    poll_tasks()
