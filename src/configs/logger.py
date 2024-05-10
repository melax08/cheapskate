import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

BASE_DIR = Path(__file__).parent.parent

LOG_DIR = BASE_DIR.parent / ".data" / os.getenv("LOG_DIR", default="logs")
LOG_FILE_PATH = LOG_DIR / "bot.log"
LOG_LEVEL = LOG_LEVELS.get(os.getenv("LOG_LEVEL", default="INFO"), logging.INFO)

LOG_FORMAT = (
    "[%(asctime)s,%(msecs)d] %(levelname)s " "[%(name)s:%(lineno)s] %(message)s"
)
LOG_DT_FORMAT = "%d.%m.%y %H:%M:%S"

LOG_WHEN = "midnight"
LOG_INTERVAL = 1
LOG_BACKUP_COUNT = 30
LOG_ENCODING = "UTF-8"


def configure_logging() -> None:
    """
    Configure global logging.
    Logging into stdout and in log_file.
    """
    LOG_DIR.mkdir(exist_ok=True, parents=True)

    rotating_handler = TimedRotatingFileHandler(
        LOG_FILE_PATH,
        backupCount=LOG_BACKUP_COUNT,
        when=LOG_WHEN,
        interval=LOG_INTERVAL,
        encoding=LOG_ENCODING,
    )

    logging.basicConfig(
        datefmt=LOG_DT_FORMAT,
        format=LOG_FORMAT,
        level=LOG_LEVEL,
        handlers=(rotating_handler, logging.StreamHandler()),
    )

    # Disable information logs from telegram API itself requests.
    logging.getLogger("httpx").setLevel(logging.WARNING)
