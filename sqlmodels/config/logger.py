import os
import logging


def setup_logger(log_file_path):
    # 确保日志目录存在
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    # 使用更灵活的配置方式而不是 basicConfig
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.INFO)

    # 文件处理器
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    logger.addHandler(file_handler)

    return logger

path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# 设置日志文件路径
log_file_path = f'{path}/log/sqlmodel/logger.log'
logger = setup_logger(log_file_path)
