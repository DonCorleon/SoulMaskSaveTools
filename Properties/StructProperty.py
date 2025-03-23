from config import *
import inspect
from .LinearColorProperty import LinearColorProperty
#from .TransformProperty import TransformProperty
from .QuatProperty import QuatProperty
from .VectorProperty import VectorProperty
from .IntProperty import IntProperty
from .GuidProperty import GuidProperty
from .NoneProperty import NoneProperty


class StructProperty:
    padding = bytes([0x00] * 4)
    unknown = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    type = "StructProperty"

    def __init__(self, name, binary_read, in_array=False):
        logger.debug(f'{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}')
        if in_array:
            logger.warning(f'{text_colours["Lime Green"]}{binary_read.offset}:Struct is part of array')
        self.type = "StructProperty"
        self.name = name
        struct_start_position = binary_read.offset
        logger.debug(binary_read.peek(20,10))
        if not in_array:
            self.content_size = binary_read.read_uint32()
        padding = binary_read.read_bytes(4)

        logger.debug(f'{text_colours["Green"]}StructProperty name:{self.name}, type:{self.type}, position:{binary_read.offset}')


        data_end_position = binary_read.offset
        logger.debug(f'{binary_read.peek(20, 10)}')

        if in_array:
            logger.warning(f'HERE struct_count: in array')

            self.subtype = binary_read.read_string()
            logger.debug(f'{text_colours["Lime Green"]}{self.subtype}')
            binary_read.read_bytes(17)
            self.value = None
            self.value = binary_read.read_property()

        else:
            self.subtype = binary_read.read_string()

            logger.debug(f'{binary_read.offset}:self.subtype:{self.subtype}')

            binary_read.read_bytes(17)
            content_end_position = binary_read.offset + self.content_size
            if self.content_size == 0:
                self.value = None
                return
            if self.subtype == "Guid":
                self.value = GuidProperty(self.name, binary_read, self.content_size)
            elif self.subtype == "DateTime":
                self.value = binary_read.read_date_time()
            elif self.subtype == "LinearColor":
                self.value = LinearColorProperty(binary_read)
            elif self.subtype in ["Quat", "Rotator"]:
                self.value = QuatProperty(self.name, binary_read)
            elif self.subtype == 'Vector':
                self.value = VectorProperty(binary_read)
            elif self.subtype == "IntProperty":
                self.value = IntProperty(self.name, binary_read)
            else:
                logger.warning(f'Unknown subtype for Struct : {self.subtype} size:{self.content_size}')
                self.value = []
                prop = None
                while not isinstance(prop, NoneProperty):
                    prop = binary_read.read_property()
                    self.value.append(prop)

                    #binary_read.read_bytes(1)
            if binary_read.offset != content_end_position:
                logger.warning(f'StructProperty read incorrectly. position:{binary_read.offset}, struct_start_position:{struct_start_position}, content_end_position:{content_end_position}')
                raise Exception(f'StructProperty read incorrectly. position:{binary_read.offset}, struct_start_position:{struct_start_position}, content_end_position:{content_end_position}')


        logger.debug(f'{text_colours["Green"]}StructProperty Complete:{self.name}, type:{self.type}, subtype:{self.subtype}, value:{self.value}')

    def __repr__(self):
        return '{}, {}, {}, {}'.format(
            self.name,
            self.type,
            self.subtype,
            self.value)
