import os

from loguru import logger

# chmod 755 logs
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logger.add(
    sink=os.path.join(BASE_DIR, 'logs/service.log'),
    rotation='500 MB',  # 日志文件最大限制500mb
    retention='30 days',  # 最长保留30天
    format="{time}|{level}|{message}",  # 日志显示格式
    compression="zip",  # 压缩形式保存
    encoding='utf-8',  # 编码
    level='INFO',  # 日志级别
)

logger.add(
    sink=os.path.join(BASE_DIR, 'logs/error.log'),
    rotation='500 MB',  # 日志文件最大限制500mb
    retention='30 days',  # 最长保留30天
    format="{time}|{level}|{message}",  # 日志显示格式
    compression="zip",  # 压缩形式保存
    encoding="utf-8",
    level='ERROR',  # 日志级别
)

if __name__ == '__main__':
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warning message')
    logger.error('error message')