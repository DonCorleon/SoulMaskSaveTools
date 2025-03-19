from config import *
import inspect


class NoneProperty:
    bytes = bytes([0x05, 0x00, 0x00, 0x00, 0x4E, 0x6F, 0x6E, 0x65, 0x00])
    type = "NoneProperty"
    def __init__(self):
        logger.debug(f'{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}')
        self.type = 'NoneProperty'

    def __repr__(self):
        return '{}'.format(
            self.type)
