from config import *
import inspect
from .NoneProperty import NoneProperty
from .StructProperty import StructProperty
from .StrProperty import StrProperty
from .TextProperty import TextProperty
from .FloatProperty import FloatProperty
from .BoolProperty import BoolProperty
from .ArrayProperty import ArrayProperty


class MapProperty:
    padding = bytes([0x00, 0x00, 0x00, 0x00])
    type = "MapProperty"

    def __init__(self, name, binary_read):
        logger.debug(f'{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}')
        self.name = name
        self.type = "MapProperty"

        self.content_size = binary_read.read_uint32()  # contentSize
        binary_read.read_bytes(len(MapProperty.padding))
        self.key_type = binary_read.read_string()

        self.value_type = binary_read.read_string()
        binary_read.read_bytes(1)
        data_end_position = self.content_size + binary_read.offset
        self.value = []
        binary_read.read_bytes(len(MapProperty.padding))
        content_count = binary_read.read_uint32()
        logger.info(f'\x1b[38;5;82mMapProperty name:{self.name}, key_type:{self.key_type}, value_type:{self.value_type} content_count:{content_count}, content_size:{self.content_size}, position:{binary_read.offset}')



        while binary_read.offset < data_end_position:
            Guid = binary_read.read_uuid()
            output = []
            next_property = None
            while not isinstance(next_property, NoneProperty):
                next_property = binary_read.read_property()
                output.append(next_property)
            self.value.append([Guid,output])



        logger.info(f'\x1b[38;5;82mEnd of MapProperty {self.name}, Position:{binary_read.offset}, data_end_position:{data_end_position}')
        #logger.debug(f'Position:{binary_read.offset}, name:{self.name}, type:{self.type}, value length:{len(self.value)}')

    def __repr__(self):
        return '{}, {}, {}, {}, {}'.format(
            self.name,
            self.type,
            self.key_type,
            self.value_type,
            self.value)
