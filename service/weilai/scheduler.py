import datetime
import time
from threading import Thread
from utils.logger import get_logger  # 自定义日志模块
from service.weilai.task import start_task  # 抢购任务主逻辑

logger = get_logger()


def run_with_schedule(authorization_list: list[str], task_lines: list[str], run_time: str = None):
    """
    支持定时启动抢购任务
    :param authorization_list: ['19912345678:token1:123456']
    :param task_lines: ['19912345678-蛇来运转-1']
    :param run_time: '2025-06-18 22:30:00'
    """
    try:
        if run_time:
            target_time = datetime.datetime.strptime(run_time, "%Y-%m-%d %H:%M:%S")
            now = datetime.datetime.now()
            wait_seconds = (target_time - now).total_seconds()
            if wait_seconds > 0:
                logger.info(f"[定时] 等待 {wait_seconds:.2f} 秒后启动抢购任务（目标时间：{run_time}）")
                time.sleep(wait_seconds)
            else:
                logger.warning(f"[定时] 指定时间 {run_time} 已过，立即执行任务")
        start_task(authorization_list, task_lines)
    except Exception as e:
        logger.error(f"[定时任务] 执行任务过程中发生异常: {e}")


def trigger_weilai_task(auth_list, task_list, run_time):
    """
    用于外部触发定时抢购任务（例如微信指令触发）
    """
    t = Thread(target=run_with_schedule, args=(auth_list, task_list, run_time))
    t.daemon = True  # 设置守护线程
    t.start()
