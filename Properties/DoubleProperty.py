from config import *
import inspect


class DoubleProperty:
    padding = bytes([0x08] + [0x00] * 8)
    type = "DoubleProperty"

    def __init__(self, name, binary_read):
        logger.debug(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}"
        )
        self.type = "DoubleProperty"
        self.name = name
        self.value = []
        length = binary_read.read_int32()
        binary_read.read_bytes(5)
        self.value.append(binary_read.read_double())

        logger.debug(
            f"DoubleProperty:{self.name}, type:{self.type}, value:{self.value}"
        )

    def __repr__(self):
        return "{}, {}, {}".format(self.name, self.type, self.value)
