from config import *

from dataclasses import dataclass
import inspect
from .NoneProperty import NoneProperty


object_types = {
                # Zero size means no magic bits
                b'\x00': 'Array',       # Array of following type
                b'\x01': 'Actor',       # Actor and blueprint template
                b'\x03': 'Component',   # Component Name, Script Name, property
                b'\x07': '',            # Actor-State, blueprint, property, None
                b'\x09': 'Name Only',   # Blueprint, property, None
}

@dataclass
class ObjectProperty:
    padding = bytes([0x00, 0x00, 0x00, 0x00, 0x00])
    type = "ObjectProperty"

    def __init__(self, name, binary_read, in_array=False):
        self.name = name
        self.type = "ObjectProperty"
        logger.debug(f'position:{binary_read.offset}, name:{self.name}, type:{self.type}, in_array:{in_array}')

        # Skip if array flag set
        if not in_array:
            content_size = binary_read.read_uint32()  # contentSize
            binary_read.read_bytes(len(self.padding))
            logger.debug(f'content_size:{content_size} : called from offset:{binary_read.offset}')
            self.object_type = binary_read.read_bytes(1)
            logger.debug(f'object_type:{self.object_type.hex()}')

        # Set it to an array byte if array flag is set
        else:
            self.object_type = b'\x00'

        #object_data_start = binary_read.offset - 1

        if self.object_type in [b'\x00']:
            self.object_type = 'Array'
            content_count = binary_read.read_uint32()
            logger.error(f'content_count:{content_count}')
            array_data = []
            for i in range(content_count):
                array_object_type = binary_read.read_bytes(1)
                logger.error(f'ObjectType Array with type:{array_object_type} @ {binary_read.offset}')
                if array_object_type in [b'\x01']:
                    self.value = 'Skipped object'

                elif array_object_type in [b'\x03']:
                    self.value = self.ComponentType(binary_read)

                elif array_object_type in [b'\x07']:
                    self.value = 'Skipped object'

                elif array_object_type in [b'\x09']:
                    self.value =self.NameType(binary_read)
                    logger.debug(f'{i}:{self.value}')
                else:
                    logger.error(f'Unknown array object type with byte:{self.object_type} @ position:{binary_read.offset}')
                    raise Exception(f'Unknown array object type with byte:{self.object_type} @ position:{binary_read.offset}')
                array_data.append(self.value)
            self.value = array_data

        elif self.object_type in [b'\x01']:
            self.object_type = 'Actor'
            object_data = binary_read.read_bytes(content_size - 1)
            self.value = 'Skipped object'

        elif self.object_type in [b'\x03']:

            object_data = self.ComponentType(binary_read)

            self.value = object_data

        elif self.object_type in [b'\x07']:
            self.object_type = 'Not Sure'
            object_data = binary_read.read_bytes(content_size - 1)
            self.value = 'Skipped object'

        elif self.object_type in [b'\x09']:
            self.object_type = 'Name'
            self.value = self.NameType(binary_read)
        else:
            logger.error(f'Unknown object type with byte:{self.object_type} @ position:{binary_read.offset}')
            raise Exception(f'Unknown object type with byte:{self.object_type} @ position:{binary_read.offset}')

        logger.critical(self.value)

    def NameType(self, binary_read):
        value = binary_read.read_string()
        return value

    def ComponentType(self, binary_read):
        logger.error(f'Starting ComponentType @ {binary_read.offset}')
        name = binary_read.read_string()
        logger.error(f'name:{name}')
        script = binary_read.read_string()
        logger.error(f'script:{script}')


        value = []
        prop = None
        while not isinstance(prop, NoneProperty):
            prop = binary_read.read_property()
            value.append(prop)

        return {'name':name, 'script':script, 'value':value}

    def __repr__(self):
        return '{}, {}, {}'.format(
            self.name,
            self.type,
            self.value)


class Object_Property:
    padding = bytes([0x00, 0x00, 0x00, 0x00, 0x00])
    type = "ObjectProperty"

    def __init__(self, name, binary_read):
        logger.debug(f'{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}')
        self.type = "ObjectProperty"
        self.name = name
        #logger.debug(binary_read.peek(30))
        content_size = binary_read.read_uint32()  # contentSize
        logger.debug(f'content_size:{content_size} : called from offset:{binary_read.offset}')
        binary_read.read_bytes(len(self.padding))
        self.position = binary_read.offset
        self.unknown_byte = binary_read.read_bytes(1)
        logger.debug(f'Ukbyte:{self.unknown_byte.hex()}')
        logger.critical(f'{self.type}    >> {self.unknown_byte.hex()} : {binary_read.offset}')

        object_data = binary_read.read_bytes(content_size - 1)
        self.value = 'Skipped object'
        '''
        #logger.info(f'Object data bypassed for type ObjectProperty')
        binary_read.dump_to_disk(object_data)
        #logger.warning(f'{self.value[:50].hex(" ",1)}')
        #logger.debug(object_data.peek(50))
        object_name = object_data.read_string()
        logger.debug(f'New objects name : {object_name}')
        #logger.debug(object_data.peek(50))
        object_subname = object_data.read_string()
        logger.debug(f'New objects subname : {object_subname}')
        #logger.debug(object_data.peek(50))
        #object_data.deserialize(has_header=False)
        '''
        logger.info(f'ObjectProperty:{self.name}, type:{self.type}, size:{content_size}, value:{self.value}')

    def __repr__(self):
        return '{}, {}, {}'.format(
            self.name,
            self.type,
            self.value)
