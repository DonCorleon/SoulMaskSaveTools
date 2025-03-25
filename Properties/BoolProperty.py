from config import *
import inspect


class BoolProperty:
    padding = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    type = "BoolProperty"

    def __init__(self, name, binary_read):
        logger.debug(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}"
        )
        self.type = "BoolProperty"
        self.name = name
        binary_read.read_bytes(len(BoolProperty.padding))
        self.value = binary_read.read_boolean()
        binary_read.read_bytes(1)

        logger.debug(f"BoolProperty:{self.name}, type:{self.type}, value:{self.value}")

    def __repr__(self):
        return "{}, {}, {}".format(self.name, self.type, self.value)
