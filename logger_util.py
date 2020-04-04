from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import logging
from os import getenv, path, mkdir, listdir, remove
from sys import stdout

from constants import GetConstants

logger = logging.getLogger(f"main.{__name__}")


def log_file_name(directory: str) -> str:
    """Generates the name for a log file based off the current time"""
    return f"{directory}{GetConstants().CLASS}.log"


def optional_make_dir(directory: str) -> None:
    """Checks if dir exists, if it doesn't we go make that directory"""
    logger.debug(f"Logging directory did not exist at {directory} and so will be generated")
    if not path.isdir(directory):
        mkdir(directory)


def logging_cleanup(capacity: int = 5) -> None:
    """If there are more than capacity log files in the directory,
        delete the oldest file until there are less than capacity
    """
    log_dir = GetConstants().LOGGING_DIR
    log_files = listdir(log_dir)
    full_paths = [f"{log_dir}{x}" for x in log_files if '.log' in x]

    while len(full_paths) >= capacity:
        oldest_file = min(full_paths, key=path.getctime)
        remove(oldest_file)
        full_paths.remove(oldest_file)
        logger.debug(f"deleted log file {oldest_file} since it is the oldest and more than {capacity} log files exist")


def logging_setup(p_logger: logging.Logger) -> None:
    """
    Sets up a file handler in the directory specified by OS variables and
    sets up a stream handler to log everything to stdout as well
    @param p_logger: The logger which we are adding these handlers to
    """
    directory = GetConstants().LOGGING_DIR
    optional_make_dir(directory)

    logging_cleanup(GetConstants().LOGGING_CAPACITY)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    p_logger.setLevel(logging.DEBUG)

    # Timed rotating file handler
    fh = TimedRotatingFileHandler(log_file_name(directory), when='S', interval=10)
    fh.suffix = '%Y_%m_%d'
    p_logger.addHandler(fh)

    # File handler
    fh = logging.FileHandler(log_file_name(directory))
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    p_logger.addHandler(fh)

    # Stream handler
    sh = logging.StreamHandler(stdout)
    sh.setFormatter(formatter)
    sh.setLevel(logging.DEBUG)
    p_logger.addHandler(sh)
