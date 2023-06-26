import logging



def create_logger():
    '''
    Create logger instance
    '''
    logging.basicConfig(filename='job-tracker.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG
                    )
    logger = logging.getLogger('mail-job-tracker')
    return logger


logger = create_logger()