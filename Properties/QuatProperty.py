from config import *
import inspect


class QuatProperty:
    def __init__(self, name, binary_read):
        self.name = name
        self.type = "QuatProperty"
        x = binary_read.read_float32()
        y = binary_read.read_float32()
        z = binary_read.read_float32()
        w = binary_read.read_float32()
        self.value = {"x": x, "y": y, "z": z, "w": w}
        logger.debug(
            f"{binary_read.offset}:QuatProperty:{self.name}, type:{self.type}, value:{self.value}"
        )

    def __repr__(self):
        return str(self.value)
