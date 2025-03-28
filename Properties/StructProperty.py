from config import *
import inspect
from .LinearColorProperty import LinearColorProperty

# from .TransformProperty import TransformProperty
from .QuatProperty import QuatProperty
from .VectorProperty import VectorProperty
from .IntProperty import IntProperty
from .GuidProperty import GuidProperty
from .NoneProperty import NoneProperty


class _StructProperty:
    padding = bytes([0x00] * 4)
    unknown = bytes(
        [
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
        ]
    )
    type = "StructProperty"

    def __init__(self, name, binary_read, in_array=False):
        logger.debug(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}"
        )
        if in_array:
            logger.warning(
                f'{text_colours["Lime Green"]}{binary_read.offset}:Struct is part of array'
            )
        self.type = "StructProperty"
        self.name = name
        struct_start_position = binary_read.offset

        self.content_size = binary_read.read_uint32()
        padding = binary_read.read_bytes(4)

        if self.content_size == 0:
            struct_name = ""

        logger.debug(
            f'{text_colours["Green"]}StructProperty name:{self.name}, type:{self.type}, position:{binary_read.offset}'
        )

        data_end_position = binary_read.offset

        logger.warning(f"data_end_position:{data_end_position}")

        if in_array:
            logger.warning(f"HERE struct_count: in array")

            self.subname = binary_read.read_string()
            self.subtype = binary_read.read_string()
            logger.debug(f'{text_colours["Lime Green"]}{self.subtype}')

        else:
            self.subtype = binary_read.read_string()

        logger.debug(f"{binary_read.offset}:self.subtype:{self.subtype}")

        binary_read.read_bytes(17)


class StructProperty:
    padding = bytes([0x00] * 4)
    unknown = bytes(
        [
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
        ]
    )
    type = "StructProperty"

    def __init__(self, name, binary_read, in_array=False):
        logger.debug(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}"
        )
        if in_array:
            logger.debug(
                f'{text_colours["Lime Green"]}{binary_read.offset}:Struct is part of array'
            )
        self.type = "StructProperty"
        self.name = name
        struct_start_position = binary_read.offset
        self.content_size = binary_read.read_uint32()
        logger.debug(f"content_size:{self.content_size}")
        if not in_array:
            padding = binary_read.read_bytes(4)
            logger.debug(f"padding:{padding}")

        logger.debug(
            f'{text_colours["Green"]}StructProperty name:{self.name}, type:{self.type}, in_array:{in_array}, content_size:{self.content_size}, position:{binary_read.offset}'
        )

        if in_array:

            self.subname = binary_read.read_string()
            logger.debug(f"self.subname:{self.subname}")
            self.subtype = binary_read.read_string()
            logger.debug(f'{text_colours["Lime Green"]}{self.subtype}')
            if not self.content_size:
                binary_read.read_bytes(8)
                self.value = binary_read.read_string()
                binary_read.read_bytes(17)
                return

        else:
            self.subtype = binary_read.read_string()
            binary_read.read_bytes(17)

        if self.content_size == 0:
            self.value = None
            return
        content_end_position = binary_read.offset + self.content_size

        if self.subtype == "Guid":
            self.value = {
                "type": self.subtype,
                "value": GuidProperty(self.name, binary_read, self.content_size),
            }
        elif self.subtype == "StructProperty":
            self.value = {
                "type": self.subtype,
                "value": StructProperty(self.subname, binary_read),
            }
        elif self.subtype == "DateTime":
            self.value = {"type": self.subtype, "value": binary_read.read_date_time()}
        elif self.subtype == "LinearColor":
            self.value = {
                "type": self.subtype,
                "value": LinearColorProperty(binary_read),
            }
        elif self.subtype in ["Quat", "Rotator"]:
            self.value = {
                "type": self.subtype,
                "value": QuatProperty(self.name, binary_read),
            }
        elif self.subtype == "Vector":
            self.value = {"type": self.subtype, "value": VectorProperty(binary_read)}
        elif self.subtype == "IntProperty":
            self.value = {
                "type": self.subtype,
                "value": IntProperty(self.name, binary_read),
            }
        else:
            logger.warning(
                f"Unknown subtype for Struct : {self.subtype} size:{self.content_size}"
            )
            self.value = []
            while binary_read.offset < content_end_position:
                prop = None
                while not isinstance(prop, NoneProperty):
                    prop = binary_read.read_property()
                    self.value.append(prop)

                # binary_read.read_bytes(1)
        if binary_read.offset != content_end_position and not in_array:
            logger.warning(
                f"StructProperty read incorrectly. position:{binary_read.offset}, struct_start_position:{struct_start_position}, content_end_position:{content_end_position}"
            )
            raise Exception(
                f"StructProperty read incorrectly. position:{binary_read.offset}, struct_start_position:{struct_start_position}, content_end_position:{content_end_position}"
            )

        logger.debug(
            f'{text_colours["Green"]}StructProperty Complete:{self.name}, type:{self.type}, subtype:{self.subtype}, value:{self.value}'
        )

    def __repr__(self):
        return "{}, {}, {}, {}".format(self.name, self.type, self.subtype, self.value)
