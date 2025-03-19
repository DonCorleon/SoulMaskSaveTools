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
            logger.warning(f'{text_colours["Lime Green"]}Struct is part of array')
        self.type = "StructProperty"
        self.name = name
        #logger.debug(binary_read.peek(20,10))
        self.content_size = binary_read.read_uint32()
        binary_read.read_bytes(4)

        logger.critical(f'{text_colours["Green"]}StructProperty name:{self.name}, type:{self.type} content_size:{self.content_size}, position:{binary_read.offset}')


        reset_offset = binary_read.offset
        logger.debug(f'{binary_read.peek(20, 10)}')

        if in_array:
            self.subtype = binary_read.read_string()
            binary_read.read_bytes(17)
            self.value = None
            if self.content_size:
                self.value = binary_read.read_property()

        else:
            self.subtype = binary_read.read_string()
            logger.debug(f'{binary_read.offset}:self.subtype:{self.subtype}')

            binary_read.read_bytes(17)
            content_end_position = binary_read.offset + self.content_size
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
                logger.debug(f'Unknown subtype for Struct : {self.subtype} size:{self.content_size}')
                self.value = []
                prop = None
                while not isinstance(prop, NoneProperty):
                    prop = binary_read.read_property()
                    self.value.append(prop)

                    #binary_read.read_bytes(1)
        logger.info(f'{text_colours["Green"]}StructProperty Complete:{self.name}, type:{self.type}, subtype:{self.subtype}, value:{self.value}')
        logger.error(f'End of StructProperty {self.name}')

    def __repr__(self):
        return '{}, {}, {}, {}'.format(
            self.name,
            self.type,
            self.subtype,
            self.value)
