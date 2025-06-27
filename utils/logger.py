import logging
import os

# 日志格式配置
DEFAULT_LOG_FORMAT = '[%(asctime)s] %(levelname)s: %(message)s'
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# 控制台颜色映射
COLOR_MAP = {
    'DEBUG': '\033[34m',     # 蓝色
    'INFO': '\033[32m',      # 绿色
    'WARNING': '\033[33m',   # 黄色
    'ERROR': '\033[31m',     # 红色
    'CRITICAL': '\033[35m',  # 紫红色
}
RESET_COLOR = '\033[0m'

class ColorFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        if levelname in COLOR_MAP:
            prefix = COLOR_MAP[levelname]
            message = super().format(record)
            return f"{prefix}{message}{RESET_COLOR}"
        return super().format(record)

def setup_logger(name, log_file, level=logging.INFO, fmt=DEFAULT_LOG_FORMAT):
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(level)
        formatter = logging.Formatter(fmt, datefmt=DEFAULT_DATE_FORMAT)
        color_formatter = ColorFormatter(fmt, datefmt=DEFAULT_DATE_FORMAT)

        # 日志文件目录
        log_dir = os.path.join(os.path.dirname(__file__), 'log')
        os.makedirs(log_dir, exist_ok=True)

        # 文件日志（无颜色）
        file_handler = logging.FileHandler(os.path.join(log_dir, log_file), encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 控制台日志（彩色）
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(color_formatter)
        logger.addHandler(stream_handler)

    return logger

def get_logger():
    return {
        'main': setup_logger("weilai_main", "weilai.log"),
        'success': setup_logger("success_logger", "success.log"),
        'request': setup_logger("request_logger", "request.log"),
        'process': setup_logger("process_logger", "process.log"),
        'order': setup_logger("order_logger", "order.log"),
        'check_token': setup_logger("check_token_logger", "check_token.log"),
        'get_task': setup_logger("get_task_logger", "get_task.log"),
        'wx_operation': setup_logger("wx_operation_logger", "wx_operation.log"),
        'wx_chat': setup_logger("wx_chat_logger", "wx_chat.log"),
    }

# 使用实例
# loggers = get_logger()
# loggers['main'].debug("这是 DEBUG 日志")
# loggers['main'].info("这是 INFO 日志")
# loggers['main'].warning("这是 WARNING 日志")
# loggers['main'].error("这是 ERROR 日志")
# loggers['main'].critical("这是 CRITICAL 日志")