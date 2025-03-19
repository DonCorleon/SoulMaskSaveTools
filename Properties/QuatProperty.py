from config import *
import inspect


class QuatProperty:
    def __init__(self, name, binary_read):
        self.name = name
        self.type = 'QuatProperty'
        x = binary_read.read_float32()
        y = binary_read.read_float32()
        z = binary_read.read_float32()
        w = binary_read.read_float32()
        self.value = {'x':x, 'y':y, 'z':z, 'w':w}
        logger.warning(f'{binary_read.offset}:QuatProperty:{self.name}, type:{self.type}, value:{self.value}')
        logger.warning(binary_read.peek(30))

    def __repr__(self):
        return str(self.value)
