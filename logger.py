import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import datetime

def setupLogging():
    log_dir = Path('logs')
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_filename = f'basketball_stats_{timestamp}.log'
    log_filepath = log_dir / log_filename

    log_format = '%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    handler = RotatingFileHandler(
        filename=str(log_filepath),
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
    )
    handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)
