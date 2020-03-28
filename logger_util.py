from datetime import datetime
import logging
from os import getenv, path, mkdir, listdir, remove
from sys import stdout

logger = logging.getLogger(__name__)


def log_file_name() -> str:
    """Generates the name for a log file based off the current time"""
    today = datetime.today()
    current_time = today.strftime("%H.%M.%m.%d.%Y")

    directory = getenv('LOGGING_DIR')
    optional_make_dir(directory)

    return f"{directory}{current_time}.log"


def optional_make_dir(directory: str) -> None:
    """Checks if dir exists, if it doesn't we go make that directory"""
    if not path.isdir(directory):
        mkdir(directory)


def logging_cleanup(capacity: int = 5) -> None:
    """If there are more than capacity log files in the directory,
        delete the oldest file until there are less than capacity
    """
    log_dir = getenv('LOGGING_DIR')
    log_files = listdir(log_dir)
    full_paths = [f"{log_dir}{x}" for x in log_files if x.endswith('.log')]

    while len(full_paths) > capacity:
        oldest_file = min(full_paths, key=path.getctime)
        logger.debug(f"Deleting log file: {oldest_file}")
        remove(oldest_file)
        full_paths.remove(oldest_file)


def logging_setup(p_logger: logging.Logger) -> None:
    """
    Sets up a file handler in the directory specified by OS variables and
    sets up a stream handler to log everything to stdout as well
    @param p_logger: The logger which we are adding these handlers to
    """
    logging_cleanup()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    p_logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(log_file_name())
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    p_logger.addHandler(fh)

    sh = logging.StreamHandler(stdout)
    sh.setFormatter(formatter)
    sh.setLevel(logging.DEBUG)
    p_logger.addHandler(sh)
