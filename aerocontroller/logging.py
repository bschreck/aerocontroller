import logging
import sys


def get_logger(name):
    logger = logging.getLogger(name)
    console = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s - aero_controller - %(levelname)s - %(message)s")
    console.setFormatter(formatter)
    logger.addHandler(console)
    logger.setLevel(logging.INFO)
    return logger
