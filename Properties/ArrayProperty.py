from config import *
import inspect

from .NoneProperty import NoneProperty
from .StructProperty import StructProperty
from.ObjectProperty import ObjectProperty

from .BoolProperty import BoolProperty
from .ByteProperty import ByteProperty
from .DoubleProperty import DoubleProperty
from .FloatProperty import FloatProperty
from .IntProperty import IntProperty
from .Int64Property import Int64Property
from .UInt32Property import UInt32Property

from .EnumProperty import EnumProperty
from .NameProperty import NameProperty
from .StrProperty import StrProperty
from .TextProperty import TextProperty


class ArrayProperty:
    padding = bytes([0x00, 0x00, 0x00, 0x00])
    unknown = bytes([0x00] * 17)
    type = "ArrayProperty"

    def __init__(self, name, binary_read):
        logger.debug(f'{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}')
        self.type = "ArrayProperty"
        self.name = name

        array_content_size = binary_read.read_uint32()
        logger.debug(f'array_content_size:{array_content_size} : called from offset:{binary_read.offset}')
        binary_read.read_bytes(len(self.padding))


        self.subtype = binary_read.read_string()
        unknown_byte = binary_read.read_bytes(1).hex()
        array_end_position = binary_read.offset + array_content_size

        logger.info(f'{text_colours["Magenta"]}ArrayProperty name:{self.name}, subtype:{self.subtype} array_content_size:{array_content_size}, position:{binary_read.offset}')

        self.value = []

        if self.subtype in ['ObjectProperty']:
            self.value = []
            while binary_read.offset < array_end_position:

                self.value.append(ObjectProperty(self.name, binary_read, in_array=True))

        elif self.subtype in ['StructProperty']:
            self.value = []
            while binary_read.offset < array_end_position:
                self.value.append(StructProperty(self.name, binary_read, in_array=True))

            '''
            struct_count = binary_read.read_int32()
            values =[]
            if struct_count < 1:
                for i in range(struct_count):
                    logger.warning(f'itteration:{i} of {struct_count}, name:{self.name}, subtype:{self.subtype}')
                    next_property = None
                    while not isinstance(next_property, NoneProperty):
                        next_property = binary_read.read_property()
                        values.append(next_property)
            self.value = values
            '''
        elif self.subtype in ['TextProperty']:
            self.value = []
            array_end_position += 9
            binary_read.read_bytes(9)
            self.value.append(binary_read.read_bytes(array_content_size))

            logger.warning(self.value)

        elif self.subtype in ['IntProperty']:
            int_content_count = binary_read.read_uint32()
            logger.debug(f'int_content_count:{int_content_count}')
            self.value = []
            for i in range(int_content_count):
                self.value.append(binary_read.read_int32())
            logger.debug(f'Array IntProperty >> name:{self.name}, type:{self.type}, subtype:{self.subtype}, value:{self.value}')
        else:
            logger.error(f'Unknown Array subtype:"{self.subtype}"')
            logger.error(binary_read.peek(20,20))
            raise Exception(f'Unknown subtype:"{self.subtype}"')

        if binary_read.offset != array_end_position:
            logger.warning(f'ArrayProperty read incorrectly. position:{binary_read.offset}, array_end_position:{array_end_position}')
            raise Exception(f'ArrayProperty read incorrectly. position:{binary_read.offset}, array_end_position:{array_end_position}')

        logger.info(f'{text_colours["Magenta"]}End of ArrayProperty {self.name}')

    def __repr__(self):
        return '{}, {}, {}'.format(
            self.name,
            self.type,
            self.value)
