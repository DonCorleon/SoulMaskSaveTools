from config import *
import inspect


class HeaderProperty:
    type = 'HeaderProperty'

    def __init__(self, binary_read):
        logger.debug(f'{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}')
        self.type = 'HeaderProperty'
        logger.debug('Reading HeaderProperty')
        self.version = binary_read.read_uint32()
        self.header = binary_read.read_string()
    def __repr__(self):
        return '{}'.format(
            self.type)
