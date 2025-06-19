# utils/logger.py
import logging
import os

def get_logger():
    # 日志目录
    log_dir = os.path.join(os.path.dirname(__file__), 'log')
    os.makedirs(log_dir, exist_ok=True)  # 确保目录存在

    # 主日志 logger
    logger = logging.getLogger("weilai_main")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        file_handler = logging.FileHandler(os.path.join(log_dir, "weilai.log"), encoding="utf-8")
        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    # 支付成功日志 logger
    success_logger = logging.getLogger("success_logger")
    if not success_logger.handlers:
        success_logger.setLevel(logging.INFO)
        success_handler = logging.FileHandler(os.path.join(log_dir, "success.log"), encoding="utf-8")
        success_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        success_handler.setFormatter(success_formatter)
        success_logger.addHandler(success_handler)

    return logger, success_logger
