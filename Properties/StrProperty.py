from config import *
import inspect


class StrProperty:
    padding = bytes([0x00] * 8)
    type = "StrProperty"

    def __init__(self, name, binary_read):
        logger.debug(
            f"{binary_read.offset}:{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}"
        )
        self.type = "StrProperty"
        self.name = name
        self.content_size = binary_read.read_int32()
        binary_read.read_bytes(5)
        # self.value = binary_read.read_bytes(self.content_size)
        self.value = binary_read.read_string()
        # binary_read.read_bytes(1)

        logger.debug(f"StrProperty:{self.name}, type:{self.type}, value:{self.value}")

        """
        self.unknown = binary_read.read_bytes(1)
        binary_read.read_bytes(len(StrProperty.padding))
        self.value, iswide = binary_read.read_string_special()
        if iswide:
            self.wide = True
        """

    def __repr__(self):
        return "{}, {}, {}, {}".format(
            self.name, self.type, self.content_size, self.value
        )
