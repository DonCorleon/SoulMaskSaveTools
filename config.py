import logging

text_colours = {
    "Red": "\x1b[38;5;1m",
    "Green": "\x1b[38;5;2m",
    "Yellow": "\x1b[38;5;3m",
    "Blue": "\x1b[38;5;4m",
    "Magenta": "\x1b[38;5;5m",
    "Cyan": "\x1b[38;5;6m",
    "White": "\x1b[38;5;7m",
    "Bright Black (Gray)": "\x1b[38;5;8m",
    "Bright Red": "\x1b[38;5;9m",
    "Bright Green": "\x1b[38;5;10m",
    "Bright Yellow": "\x1b[38;5;11m",
    "Bright Blue": "\x1b[38;5;12m",
    "Bright Magenta": "\x1b[38;5;13m",
    "Bright Cyan": "\x1b[38;5;14m",
    "Bright White": "\x1b[38;5;15m",
    "Deep Blue": "\x1b[38;5;27m",
    "Bright Green (Alt)": "\x1b[38;5;46m",
    "Lime Green": "\x1b[38;5;82m",
    "Bright Red (Alt)": "\x1b[38;5;196m",
    "Pink": "\x1b[38;5;201m",
    "Bright Yellow (Alt)": "\x1b[38;5;226m"
}


class CustomFormatter(logging.Formatter):

    green = '\x1b[18;32m'
    grey = '\x1b[18;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'
    format = '%(asctime)s - %(levelname)s - %(filename)s >> %(module)s.%(funcName)s - %(message)s'



    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: blue + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# create console handler with a higher log level
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.INFO)
#logger.setLevel(logging.ERROR)

if __name__=='__main__':
    logger.debug('debug')
    logger.info('info')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')
