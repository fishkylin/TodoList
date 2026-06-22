# 日志初始化：app.log（全量）+  error.log（只错误）
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")

def setup_logging(level:str = "INFO") -> None:
    """初始化日志。

    三个 handler（级别从低到高）：
    - DEBUG    详细的诊断信息（--debug 开启）
    - INFO     关键操作记录（添加、删除等）
    - WARNING  可恢复的问题（JSON 损坏回退）
    - ERROR    操作失败

    输出目标：
    - app_handler  → logs/app.log   (DEBUG+, 10MB × 5)
    - err_handler  → logs/error.log (ERROR+, 10MB × 5)
    - console      → stderr (WARNING+, --debug 时 DEBUG+)
    """
    LOG_DIR.mkdir(exist_ok=True)
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    if root_logger.handlers:
        return

    app_handler = RotatingFileHandler(
        filename=LOG_DIR / "app.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    app_handler.setLevel(logging.DEBUG)
    app_handler.setFormatter(fmt)

    error_handler = RotatingFileHandler(
        filename=LOG_DIR / "error.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(fmt)

    console_handler = logging.StreamHandler()
    if level == "DEBUG":
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(fmt)

    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)

    # 记录一条启动日志，表示日志系统已就绪
    root_logger.info(f"Logging initialized (debug={level})")

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)