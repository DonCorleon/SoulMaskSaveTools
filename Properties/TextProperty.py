from config import *
import inspect


class TextProperty:
    padding = bytes([0x00] * 4)
    type = "StrProperty"

    def __init__(self, name, binary_read):
        start_pos = binary_read.offset
        logger.debug(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}"
        )
        self.type = "TextProperty"
        self.name = name
        # Length of data field
        content_length = binary_read.read_uint32()
        padding = binary_read.expect(self.padding)
        # Null terminator
        binary_read.expect(b"\x00")
        expected_end_position = binary_read.offset + content_length

        self.value = binary_read.read_bytes(content_length)

        # logger.debug(f'TextProperty:{self.name}, type:{self.type}, ukInt:{self.unknown_int}, ukdata:{self.unknown_data}')
        logger.warning(
            f"TextProperty:{self.name}, type:{self.type}, value:{self.value}"
        )

    def __repr__(self):
        return "{}, {}, {}".format(self.name, self.type, self.value)


if __name__ == "__main__":
    TextProperties = [
        "0D 00 00 00 54 65 78 74 50 72 6F 70 65 72 74 79 00 43 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00 21 00 00 00 38 31 32 45 35 32 34 34 34 30 31 44 44 46 41 30 41 31 44 42 43 42 39 30 33 39 46 45 31 31 33 42 00 F8 FF FF FF B3 6C 37 8C 30 57 57 90 F9 8F 30 57 AB 5B 00 00",
        "0D 00 00 00 54 65 78 74 50 72 6F 70 65 72 74 79 00 09 00 00 00 00 00 00 00 00 00 00 00 00 FF 00 00 00 00",
        "0D 00 00 00 54 65 78 74 50 72 6F 70 65 72 74 79 00 E9 00 00 00 00 00 00 00 00 01 00 00 00 02 08 00 00 00 00 03 00 00 00 57 53 00 10 00 00 00 42 75 4C 75 6F 44 69 57 65 69 5A 68 69 59 65 00 0A 00 00 00 7B 30 7D 7B 31 7D 7B 32 7D 00 03 00 00 00 04 00 00 00 00 00 01 00 00 00 00 21 00 00 00 35 34 39 38 32 38 43 36 34 41 33 36 34 35 41 41 36 38 36 36 45 37 41 43 31 33 44 42 42 31 43 35 00 FB FF FF FF 6B 70 F3 77 E8 90 3D 84 00 00 04 00 00 00 00 00 01 00 00 00 00 21 00 00 00 39 42 45 36 36 41 35 39 34 46 39 34 44 36 33 31 37 36 30 30 38 41 41 34 32 35 43 35 31 30 38 37 00 FD FF FF FF 4E 4F 36 96 00 00 04 00 00 00 00 00 01 00 00 00 00 21 00 00 00 45 36 30 31 30 46 32 33 34 43 43 44 36 42 34 44 44 42 39 30 42 42 42 36 43 41 43 36 41 37 35 35 00 FD FF FF FF 18 62 EB 58 00 00",
        "",
    ]

"""
0D 00 00 00 54 65 78 74 50 72 6F 70 65 72 74 79 00  # TextProperty String
09 00 00 00  # Int Total Length
00 00 00 00  # Int ? Num Items?
00  # Flag ?
00 00 00 00 
FF 00 00 00 00



0D 00 00 00 54 65 78 74 50 72 6F 70 65 72 74 79 00 
43 00 00 00 
00 00 00 00 
00 00 00 00 
00 00 01 00 00 00 00 
21 00 00 00 38 31 32 45 35 32 34 34 34 30 31 44 44 46 41 30 41 31 44 42 43 42 39 30 33 39 46 45 31 31 33 42 00 
F8 FF FF FF B3 6C 37 8C 30 57 57 90 F9 8F 30 57 AB 5B 00 00
"""
