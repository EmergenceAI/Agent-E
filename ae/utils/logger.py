import logging

logger = logging.getLogger(__name__)
'''logging.basicConfig(
    level=logging.DEBUG, # change level here or use set_log_level() to change it
    format="[%(asctime)s] %(levelname)s {%(filename)s:%(lineno)d}  - %(message)s", filename='app.log', filemode='a'
)'''
logging.basicConfig(level=logging.INFO)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("matplotlib.pyplot").setLevel(logging.WARNING)
logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING)
logging.getLogger("PIL.Image").setLevel(logging.WARNING)

def set_log_level(level: str | int) -> None:
    """
    Set the log level for the logger.

    Parameters:
    - level (Union[str, int]): A string or logging level such as 'debug', 'info', 'warning', 'error', or 'critical', or the corresponding logging constants like logging.DEBUG, logging.INFO, etc.
    """
    if isinstance(level, str):
        level = level.upper()
        numeric_level = getattr(logging, level, None)
        if not isinstance(numeric_level, int):
            raise ValueError(f'Invalid log level: {level}')
        logger.setLevel(numeric_level)
    else:
        logger.setLevel(level)
