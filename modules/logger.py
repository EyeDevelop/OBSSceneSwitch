import logging


def get_logger(level: int, mod_name: str) -> logging.Logger:
    """
    Creates a logger object used for easy logging.

    :return: The logger object.
    """

    # Setup the logging object.
    logger = logging.getLogger(mod_name)
    if logger.hasHandlers():
        return logger

    logger.setLevel(level)

    # Add a StreamHandler and format it.
    fmt = logging.Formatter("[%(asctime)s : %(levelname)s : %(module)s] : %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(fmt)
    logger.addHandler(console_handler)

    # Return the logger.
    return logger
