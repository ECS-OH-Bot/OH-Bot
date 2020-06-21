from email.message import EmailMessage
from logging.handlers import TimedRotatingFileHandler, QueueHandler, QueueListener, SMTPHandler
import logging
from queue import Queue
from os import path, mkdir, listdir, remove
from smtplib import SMTP_SSL
from sys import stdout

from constants import GetConstants

logger = logging.getLogger(f"main.{__name__}")


class SelfCleaningRotatingTimedFileHandler(TimedRotatingFileHandler):
    """
    File handler that changes to a new file at midnight. When it does
    this it also goes and cleans up the directory that contains the log
    files
    """

    def __init__(self, filename, when='midnight', interval=1):
        super().__init__(filename, when=when, interval=interval)

    def doRollover(self) -> None:
        logging_cleanup()
        super().doRollover()


class SSLSMTPHandler(SMTPHandler):
    def __init__(self, mailhost, fromaddr, toaddrs, subject, **kwargs):
        super().__init__(mailhost, fromaddr, toaddrs, subject, **kwargs)
        self.mailhost = mailhost
        self.fromaddr = fromaddr
        self.toaddrs = toaddrs
        self.subject = subject

    def emit(self, record: logging.LogRecord) -> None:
        msg = EmailMessage()
        msg['To'] = self.toaddrs
        msg['From'] = self.fromaddr
        msg['Subject'] = self.subject
        msg.set_content(self.format(record))

        with SMTP_SSL(GetConstants().SMTP_HOST, 465) as server:
            server.ehlo()
            server.login(GetConstants().USERNAME, GetConstants().PASSWORD)
            server.send_message(msg)


def log_file_name(directory: str) -> str:
    """Generates the name for a log file based off the current time"""
    return f"{directory}{GetConstants().CLASS}.log"


def optional_make_dir(directory: str) -> None:
    """Checks if dir exists, if it doesn't we go make that directory"""
    if not path.isdir(directory):
        logger.debug(f"Logging directory did not exist at {directory} and so will be generated")
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
    handlers = []

    directory = GetConstants().LOGGING_DIR
    optional_make_dir(directory)

    logging_cleanup(GetConstants().LOGGING_CAPACITY)

    formatter = logging.Formatter('%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s')

    p_logger.setLevel(logging.DEBUG)

    # Timed rotating file handler
    fh = SelfCleaningRotatingTimedFileHandler(log_file_name(directory))
    fh.suffix = '%Y_%m_%d.log'
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    handlers.append(fh)

    # Stream handler
    sh = logging.StreamHandler(stdout)
    sh.setFormatter(formatter)
    sh.setLevel(logging.DEBUG)
    handlers.append(sh)

    # Email Handler
    # Only initialize the handler if we're given information
    if GetConstants().SMTP_HOST and GetConstants().MAILING_LIST and GetConstants().USERNAME and GetConstants().PASSWORD:
        eh = SSLSMTPHandler(GetConstants().SMTP_HOST, f"{GetConstants().CLASS} OH Bot <your_friendly_bot@discord>",
                            GetConstants().MAILING_LIST,
                            "A CRITICAL ERROR HAS OCCURRED")
        eh.setFormatter(formatter)
        eh.setLevel(logging.CRITICAL)
        handlers.append(eh)

    queue = Queue(-1)
    qh = QueueHandler(queue)
    q_listener = QueueListener(queue, *handlers, respect_handler_level=True)
    p_logger.addHandler(qh)
    q_listener.start()
