from config import *
import inspect


class IntProperty:
    padding = bytes([0x04] + [0x00] * 8)
    type = 'IntProperty'

    def __init__(self, name, binary_read):
        self.type = "IntProperty"
        self.name = name
        binary_read.read_bytes(len(IntProperty.padding))
        self.value = binary_read.read_int32()

        logger.debug(f'IntProperty:{self.name}, type:{self.type}, value:{self.value}')

    def __repr__(self):
        return '{}, {}, {}'.format(
            self.name,
            self.type,
            self.value)
