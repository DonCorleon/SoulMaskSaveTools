from config import *
import inspect


class UInt32Property:
    padding = bytes([0x04] + [0x00] * 8)
    type = "UInt32Property"

    def __init__(self, name, binary_read):
        logger.debug(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}"
        )
        self.type = "UInt32Property"
        self.name = name
        binary_read.read_bytes(len(UInt32Property.padding))
        self.value = binary_read.read_uint32()

        logger.debug(
            f"UInt32Property:{self.name}, type:{self.type}, value:{self.value}"
        )

    def __repr__(self):
        return "{}, {}, {}".format(self.name, self.type, self.value)
