import logging
from pathlib import Path
import datetime


def setupLogging():
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"basketball_stats_{timestamp}.log"
    log_filepath = log_dir / log_filename

    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        filename=str(log_filepath),
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
    )
