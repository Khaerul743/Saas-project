import logging
import sys
from logging.handlers import RotatingFileHandler

from colorama import Fore, Style, init

# Init colorama biar cross-platform
init(autoreset=True)

# Format log standar: timestamp | level | module | message
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

# Warna untuk tiap level log
LEVEL_COLORS = {
    "DEBUG": Fore.CYAN,
    "INFO": Fore.GREEN,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": Fore.MAGENTA + Style.BRIGHT,
}


class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_fmt = LOG_FORMAT
        formatter = logging.Formatter(log_fmt)
        formatted = formatter.format(record)

        # Tambahin warna sesuai level
        color = LEVEL_COLORS.get(record.levelname, "")
        return color + formatted + Style.RESET_ALL


def get_logger(name: str) -> logging.Logger:
    """
    Utility untuk dapetin logger dengan format konsisten + warna di console.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    # Console handler (warna di terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColorFormatter())
    logger.addHandler(console_handler)

    # File handler (tetap tanpa warna)
    file_handler = RotatingFileHandler(
        "logs/app.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)

    return logger
