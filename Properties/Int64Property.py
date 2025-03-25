from config import *
import inspect


class Int64Property:
    padding = bytes([0x08] + [0x00] * 8)
    type = "Int64Property"

    def __init__(self, name, binary_read):
        logger.debug(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}"
        )
        self.type = "Int64Property"
        self.name = name
        binary_read.read_bytes(len(Int64Property.padding))
        self.value = binary_read.read_int64()

        logger.debug(
            f"Int64Property:{self.name}, type:{self.type},, value:{self.value}"
        )

    def __repr__(self):
        return "{}, {}, {}".format(self.name, self.type, self.value)
