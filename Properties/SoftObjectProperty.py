from config import *
import inspect


class SoftObjectProperty:
    padding = bytes([0x00, 0x00, 0x00, 0x00, 0x00])
    type = "SoftObjectProperty"

    def __init__(self, name, binary_read):
        logger.debug(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}"
        )
        self.type = "SoftObjectProperty"
        self.name = name
        content_size = binary_read.read_uint32()  # contentSize
        binary_read.read_bytes(len(SoftObjectProperty.padding))
        self.value = binary_read.read_string()
        binary_read.read_bytes(4)

    def __repr__(self):
        return "{}, {}, {}".format(self.name, self.type, self.value)
