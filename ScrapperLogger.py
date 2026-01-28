import logging
import os

class NoErrorFilter(logging.Filter):
    def filter(self, record):
        return record.levelno < logging.ERROR

def setup_logging():

    logger = logging.getLogger("ScrapperLogger")
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("scraper_log.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s'))
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.addFilter(NoErrorFilter())
    console_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger