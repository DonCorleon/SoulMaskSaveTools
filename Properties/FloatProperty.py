from config import *
import inspect


class FloatProperty:
    padding = bytes([0x00] * 4)

    def __init__(self, name, binary_read, in_array=False):
        logger.debug(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}"
        )
        self.type = "FloatProperty"
        self.name = name
        if not in_array:
            # Length of data field
            content_length = binary_read.read_uint32()
            padding = binary_read.expect(self.padding)
            # Null terminator
            binary_read.expect(b"\x00")
            expected_end_position = binary_read.offset + content_length
        self.value = binary_read.read_float32()

        if not in_array:
            if binary_read.offset != expected_end_position:
                logger.error(
                    f"FloatProperty did not read correctly. Finished at {binary_read.offset}, expected {expected_end_position}"
                )
                raise Exception(
                    f"FloatProperty did not read correctly. Finished at {binary_read.offset}, expected {expected_end_position}"
                )

        logger.debug(f"FloatProperty:{self.name}, type:{self.type}, value:{self.value}")

    def __repr__(self):
        return "{}, {}, {}".format(self.name, self.type, self.value)
