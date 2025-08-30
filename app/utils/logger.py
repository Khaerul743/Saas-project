import logging
import sys
from logging.handlers import RotatingFileHandler

# Format log: timestamp | level | module | message
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def get_logger(name: str) -> logging.Logger:
    """
    Utility untuk dapetin logger dengan format konsisten.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)  # default INFO, bisa diubah ke DEBUG

    # Kalau logger udah ada handler, jangan duplicate
    if logger.handlers:
        return logger

    # Console handler (biar keliatan di terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)

    # File handler (rotate kalau size > 5MB, simpan 3 file lama)
    file_handler = RotatingFileHandler(
        "logs/app.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)

    return logger
