import logging


def setup_custom_logger(name):
    """
    Usage:
        logger = utils.setup_custom_logger('Nameoflogger')
    :param name: string, name of logger
    :return: None
    """
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger
