import os
import logging
from flask import Blueprint, request
from flask import current_app as app
from utils import safe_mkdir, dump_to_json, get_base_dir


app_log = Blueprint('log', __name__)
LOGGER_NAME_PREFIX = __name__ + '.'


def log_request(request, name):
    """ Log request with particular logger (to corresponding file) """
    logger = logging.getLogger(LOGGER_NAME_PREFIX + name)
    logger.info('=================')
    logger.info('Method: {method}'.format(method=request.method))
    # headers from WSGI environment are not sorted
    headers = dump_to_json(dict(request.headers))
    logger.info('---- Headers ----\n' + headers)
    if request.is_json:
        json = dump_to_json(request.get_json())
        logger.info('---- JSON ----\n' + json)
    else:
        data = request.get_data().decode()
        logger.info('---- Data ----\n' + data)


# Setup loggers
# =============


# explicitly name default logger, because a logger names will matched to a file
# names
@app_log.record
def name_default_logger(setup_state):
    setup_state.app.config['LOGGER_NAME'] = LOGGER_NAME_PREFIX + 'default'


@app_log.before_app_first_request
def setup_loggers():
    logdir = os.path.join(get_base_dir(), 'log')
    safe_mkdir(logdir)

    def setup_file_logger(logger):
        short_name = logger.name[len(LOGGER_NAME_PREFIX):]
        file = os.path.join(logdir, '{name}.log'.format(name=short_name))
        fileHandler = logging.FileHandler(file)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)

    setup_file_logger(app.logger)

    # set logger class for future loggers
    class RequestLogger(logging.Logger):
        def __init__(self, name):
            super(RequestLogger, self).__init__(name)
            setup_file_logger(self)
            self.setLevel(logging.INFO)
    logging.setLoggerClass(RequestLogger)


@app_log.before_app_request
def log_all_requests():
    log_request(request, 'requests')
