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
        logger.info(f'position:{binary_read.offset}, name:{self.name}, type:{self.type}, in_array:{in_array}')

        # Skip if array flag set
        if not in_array:
            content_size = binary_read.read_uint32()  # contentSize
            binary_read.read_bytes(len(self.padding))
            logger.debug(f'content_size:{content_size} : called from offset:{binary_read.offset}')
            end_pos = binary_read.offset + content_size
            self.object_type = binary_read.read_bytes(1)
            logger.debug(f'object_type:{self.object_type.hex()}')

            logger.critical(f'{text_colours["Blue"]}ObjectProperty name:{self.name}, type:{object_types[self.object_type]} content_size:{content_size}, position:{binary_read.offset}')
        # Set it to an array byte if array flag is set
        else:
            self.object_type = b'\x00'
            #logger.critical(f'{text_colours["Blue"]}ObjectProperty name:{self.name}, type:{object_types[self.object_type]} in Array')





        if self.object_type in [b'\x00']:
            self.object_type = 'Array'
            num_objects_in_array = binary_read.read_uint32()

            logger.debug(f'object_content_size:{num_objects_in_array}, position:{binary_read.offset}, ')

            #exit()

            array_data = []
            for _ in range(num_objects_in_array):
            #for _ in range(1):
                array_object_type = binary_read.read_bytes(1)
                logger.warning(f'ObjectType Array with type:{array_object_type.hex()} @ {binary_read.offset}')
                if array_object_type not in [b'\x01', b'\x03', b'\x07', b'\x09']:
                    logger.warning(f'{array_object_type.hex()}Not found. Trying to read extra bytes to work out object')
                    binary_read.read_bytes(4)
                    array_object_type = binary_read.read_bytes(1)
                    logger.warning(f'Trying {array_object_type.hex()} from position {binary_read.offset - 1}')
                    if array_object_type not in [b'\x01', b'\x03', b'\x07', b'\x09']:
                        logger.error(f'Unknown array object type with byte:"{array_object_type.hex()}" @ position:{binary_read.offset}, Attempted extra byte')
                        raise Exception(f'Unknown array object type with byte:"{array_object_type.hex()}" @ position:{binary_read.offset}, Attempted extra byte')

                if array_object_type in [b'\x01']:
                    self.value = 'Skipped object'

                elif array_object_type in [b'\x03']:
                    self.value = self.ComponentType(binary_read)

                elif array_object_type in [b'\x07']:
                    self.value = 'Skipped object'

                elif array_object_type in [b'\x09']:
                    self.value = self.NameType(binary_read)
                    value = []
                    prop = None
                    while not isinstance(prop, NoneProperty):
                        prop = binary_read.read_property(in_array=True)
                        value.append(prop)
                    length = self.find_extra_data_length(binary_read)
                    logger.warning(length)
                    self.extra_data = binary_read.read_bytes(length)
                    logger.debug(f'{self.value}')

                else:
                    logger.error(f'Unknown array object type with byte:"{array_object_type.hex()}" @ position:{binary_read.offset}')
                    raise Exception(f'Unknown array object type with byte:"{array_object_type.hex()}" @ position:{binary_read.offset}')

                array_data.append(self.value)
            self.value = array_data
            binary_read.read_bytes(4)

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

        logger.critical(f'{text_colours["Blue"]}Object Complete:{self.name}, {self.object_type}, {self.value}')



    def NameType(self, binary_read):
        value = binary_read.read_string()
        return value

    def ComponentType(self, binary_read):
        logger.error(f'Starting ComponentType @ {binary_read.offset}')
        name = binary_read.read_string()
        logger.debug(f'name:{name}')
        script = binary_read.read_string()
        logger.debug(f'script:{script}')

        value = []
        prop = None
        while not isinstance(prop, NoneProperty):
            prop = binary_read.read_property(in_array=True)
            value.append(prop)
        length = self.find_extra_data_length(binary_read)
        logger.warning(length)
        extra_data = binary_read.read_bytes(length)
        return {'name': name, 'script': script, 'value': value, 'extra_data':extra_data}

    def find_extra_data_length(self, binary_read):
        starting_position = binary_read.offset
        stream_end_position = len(binary_read.file_array_buffer)
        while binary_read.offset < stream_end_position:
            next_byte = binary_read.read_bytes(1, quiet=True)
            if next_byte == b'/':
                get_position = binary_read.offset
                identifier = binary_read.read_bytes(5, quiet=True)
                if identifier == b'Game/':
                    binary_read.offset = starting_position
                    return get_position - 6 - starting_position
                else:
                    binary_read.offset = get_position
        binary_read.offset = starting_position
        return stream_end_position - starting_position
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
