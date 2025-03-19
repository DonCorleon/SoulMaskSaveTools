from config import *
import inspect


class NameProperty:
    padding = bytes([0x00] * 8)
    type = "NameProperty"

    def __init__(self, name, binary_read):
        logger.debug(f'{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}')
        self.type = "NameProperty"
        self.name = name
        self.unknown = binary_read.read_bytes(1)
        binary_read.read_bytes(len(NameProperty.padding))
        self.value = binary_read.read_string()

        logger.debug(f'NameProperty:{self.name}, type:{self.type}, ukbyte:{self.unknown}, value:{self.value}')


    def __repr__(self):
        return '{}, {}, {}, {}'.format(
            self.name,
            self.type,
            self.value,
            self.unknown)
