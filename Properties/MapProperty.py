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
        data_end_position = binary_read.offset + binary_read.offset
        self.value = []
        binary_read.read_bytes(len(MapProperty.padding))
        content_count = binary_read.read_uint32()
        logger.critical(f'\x1b[18;32mMapProperty name:{self.name}, key_type:{self.key_type}, value_type:{self.value_type} content_count:{content_count}, content_size:{self.content_size}, position:{binary_read.offset}')



        while binary_read.offset < data_end_position:
            Guid = binary_read.read_uuid()
            output = []
            next_property = None
            while not isinstance(next_property, NoneProperty):
                next_property = binary_read.read_property()
                output.append(next_property)
            '''
            name = binary_read.read_string()

            type = binary_read.read_string()

            if type == "StructProperty":
                data = StructProperty(name, binary_read)
            elif type == 'StrProperty':
                data = StrProperty(name, binary_read)
            elif type == 'TextProperty':
                data = TextProperty(name, binary_read)
            elif type == 'FloatProperty':
                data = FloatProperty(name, binary_read)
            elif type == 'BoolProperty':
                data = BoolProperty(name, binary_read)
            elif type == 'ArrayProperty':
                data = ArrayProperty(name, binary_read)
            else:
                raise Exception(f"Key Type not implemented: {type}")
            
            logger.debug(data)
            '''
            self.value.append([Guid,output])



        logger.error(f'End of MapProperty {self.name}')
        '''
            current_key = None
            current_value = None

            if self.key_type == None:
                self.key_type = binary_read.read_string()
                self.value_type = binary_read.read_string()

            if self.key_type == "StructProperty":
                current_key = binary_read.read_uuid()
            elif self.key_type == "IntProperty":
                current_key = binary_read.read_int32()
            elif self.key_type in ["StrProperty","NameProperty"]:
                current_key = binary_read.read_string()
            else:
                raise Exception(f"Key Type not implemented: {self.key_type}")

            if self.value_type == "StructProperty":
                current_value = binary_read.read_string()
            elif self.value_type == "IntProperty":
                current_value = binary_read.read_int32()
            elif self.value_type == "UInt32Property":
                current_value = binary_read.read_uint32()
            elif self.value_type == "FloatProperty":
                current_value = binary_read.read_float32()
            elif self.value_type in ["StrProperty", "EnumProperty"]:
                current_value = binary_read.read_string()
            elif self.value_type == "BoolProperty":
                current_value = bool(binary_read.read_bytes(1)[0])
            else:
                raise Exception(f"Value Type not implemented: {self.value_type}")

            self.value.append([current_key, current_value])
            self.key_type = None
            '''
        logger.debug(f'Position:{binary_read.offset}, name:{self.name}, type:{self.type}, value length:{len(self.value)}')

    def __repr__(self):
        return '{}, {}, {}, {}, {}'.format(
            self.name,
            self.type,
            self.key_type,
            self.value_type,
            self.value)
