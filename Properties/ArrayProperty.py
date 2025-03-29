from config import *
import inspect

from .NoneProperty import NoneProperty
from .StructProperty import StructProperty
from .ObjectProperty import ObjectProperty

from .BoolProperty import BoolProperty
from .ByteProperty import ByteProperty
from .DoubleProperty import DoubleProperty
from .FloatProperty import FloatProperty
from .IntProperty import IntProperty
from .Int64Property import Int64Property

from .EnumProperty import EnumProperty
from .NameProperty import NameProperty
from .StrProperty import StrProperty
from .TextProperty import TextProperty


class ArrayProperty:
    padding = bytes([0x00, 0x00, 0x00, 0x00])
    unknown = bytes([0x00] * 17)
    type = "ArrayProperty"

    def __init__(self, name, binary_read):
        STRUCT_INDENT_COUNTER["array"] += 1
        logger.debug(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}"
        )
        self.type = "ArrayProperty"
        self.name = name

        # Start of the array
        array_start_position = binary_read.offset

        # Total size of all array data
        array_content_size = binary_read.read_uint32()

        unknown_int = binary_read.read_int32()

        # Type of data in the array
        self.subtype = binary_read.read_string()

        # null_terminator
        binary_read.expect(b"\x00")

        array_end_position = binary_read.offset + array_content_size

        self.value = []

        array_count = binary_read.read_int32()

        if self.subtype == "ObjectProperty":
            for _ in range(array_count):

                self.value.append(
                    {
                        "type": self.subtype,
                        "value": ObjectProperty(self.name, binary_read, in_array=True),
                    }
                )

        elif self.subtype == "StructProperty":
            self.value = StructProperty(self.name, binary_read, in_array=True)

        elif self.subtype == "IntProperty":
            for _ in range(array_count):
                self.value.append(IntProperty(self.name, binary_read, in_array=True))

        elif self.subtype == "FloatProperty":
            for _ in range(array_count):
                self.value.append(FloatProperty(self.name, binary_read, in_array=True))

        elif self.subtype == "DoubleProperty":
            for _ in range(array_count):
                self.value.append(DoubleProperty(self.name, binary_read, in_array=True))

        elif self.subtype == "EnumProperty":
            raise Exception(
                f"Found an Enum in an array at position {binary_read.offset}"
            )

        elif self.subtype == "TextProperty":
            self.value.append(
                {
                    "type": self.subtype,
                    "value": binary_read.read_bytes(
                        array_content_size - 4
                    ),  # subtract the bytes we have used since getting the end position
                }
            )
            """
            # logger.warning(self.value)
            prop = binary_read.read_property()
            if not isinstance(prop, NoneProperty):
                logger.error(f"Not a NoneProperty {prop}")
                raise Exception(f"Not a NoneProperty {prop}")
            """
        else:
            logger.error(f"Unimplemented Array subtype : {self.subtype}")
            raise Exception(f"Unimplemented Array subtype : {self.subtype}")

        if binary_read.offset > array_end_position:
            raise Exception(
                f"Overread array {self.name} that started at {array_start_position} and ends at {array_end_position}. {binary_read.offset}"
            )

        STRUCT_INDENT_COUNTER["array"] -= 1
        logger.info(
            f'{text_colours["Magenta"]}End of ArrayProperty {self.name}, {STRUCT_INDENT_COUNTER}'
        )

    def __repr__(self):
        return "{}, {}, {}".format(self.name, self.type, self.value)


"""
        elif self.subtype in ["StructProperty"]:
            struct_name = binary_read.read_string()
            self.value = []
            for _ in range(array_count):
                self.value.append(
                    {
                        "type": self.subtype,
                        "value": StructProperty(self.name, binary_read, in_array=True),
                    }
                )

        else:
            logger.error(f'Unknown Array subtype:"{self.subtype}"')
            logger.error(binary_read.peek(20, 20))
            raise Exception(f'Unknown subtype:"{self.subtype}"')

        binary_read.expect_NoneType()

        if binary_read.offset != array_end_position:
            logger.warning(
                f"ArrayProperty read incorrectly. position:{binary_read.offset}, array_end_position:{array_end_position}"
            )
            raise Exception(
                f"ArrayProperty read incorrectly. position:{binary_read.offset}, array_end_position:{array_end_position}"
            )

        
"""


"""
Data Structure

0F 00 00 00 57 68 69 63 68 42 75 69 6C 64 4F 6E 4D 65 00 
Array Name :: ReadString

0E 00 00 00 41 72 72 61 79 50 72 6F 70 65 72 74 79 00 
Data Type:ArrayProperty :: ReadString

4C 00 00 00 
Array data length

00 00 00 00 
Possibly padding or int


0F 00 00 00 53 74 72 75 63 74 50 72 6F 70 65 72 74 79 00
Data type that is in the Array

skip byte 

    # array length is from here

----------- In the data type --------

item count - int

null terminator - skip byte
"""
