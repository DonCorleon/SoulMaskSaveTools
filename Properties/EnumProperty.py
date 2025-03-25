from config import *
import inspect


class EnumProperty:
    padding = bytes([0x00, 0x00, 0x00, 0x00])
    type = "EnumProperty"

    def __init__(self, name, binary_read):
        logger.debug(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}"
        )
        self.type = "EnumProperty"
        self.name = name
        content_length = binary_read.read_uint32()
        binary_read.read_bytes(len(EnumProperty.padding))

        # self.value = [binary_read.read_string() for _ in range(content_count)]

        self.enum = binary_read.read_string()
        binary_read.read_bytes(1)
        self.value = binary_read.read_string()

        logger.debug(
            f"ENumProperty:{self.name}, type:{self.type}, subname:{self.enum}, value:{self.value}"
        )

    def __repr__(self):
        return "{}, {}, {}, {}".format(self.name, self.type, self.enum, self.value)
