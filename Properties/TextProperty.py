from config import *
import inspect


class TextProperty:
    padding = bytes([0x00] * 8)
    type = "StrProperty"

    def __init__(self, name, binary_read):
        start_pos = binary_read.offset
        logger.debug(f'{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}')
        self.type = "TextProperty"
        self.name = name
        self.unknown_int = binary_read.read_int32()  # ?Data length
        self.unknown_data = binary_read.read_bytes(5 + self.unknown_int)
        #self.value = binary_read.read_string()

        '''
        self.unknown = binary_read.read_bytes(1)
        binary_read.read_bytes(len(StrProperty.padding))
        self.value, iswide = binary_read.read_string_special()
        if iswide:
            self.wide = True
        '''
        logger.debug(f'TextProperty:{self.name}, type:{self.type}, ukInt:{self.unknown_int}, ukdata:{self.unknown_data}')

    def __repr__(self):
        return '{}, {}, {}'.format(
            self.name,
            self.type,
            self.unknown_data)
