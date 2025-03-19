from config import *
import inspect


class FloatProperty:
    padding = bytes([0x04] + [0x00] * 8)
    type = "FloatProperty"

    def __init__(self, name, binary_read):
        logger.debug(f'{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}')
        self.type = "FloatProperty"
        self.name = name
        binary_read.read_bytes(len(FloatProperty.padding))
        self.value = binary_read.read_float32()

        logger.debug(f'FloatProperty:{self.name}, type:{self.type}, value:{self.value}')

    def __repr__(self):
        return '{}, {}, {}'.format(
            self.name,
            self.type,
            self.value)
