from config import *

from dataclasses import dataclass
import inspect
from .NoneProperty import NoneProperty


object_types = {
    # Zero size means no magic bits
    b"\x00": "Array",  # Array of following type
    b"\x01": "Actor",  # Actor and blueprint template
    b"\x03": "Component",  # Component Name, Script Name, property
    b"\x07": "",  # Actor-State, blueprint, property, None
    b"\x09": "Name Only",  # Blueprint, property, None
}


@dataclass
class ObjectProperty:
    padding = bytes([0x00, 0x00, 0x00, 0x00, 0x00])
    type = "ObjectProperty"

    def __init__(self, name, binary_read, in_array=False, object_list=False):
        STRUCT_INDENT_COUNTER["object"] += 1
        self.name = name
        self.type = "ObjectProperty"
        self.in_array = in_array
        self.object_list = object_list
        logger.error(
            f'{text_colours["Blue"]}ObjectProperty name:position:{binary_read.offset}, name:{self.name}, type:{self.type}, in_array:{in_array}, object_list:{object_list}'
        )

        # Skip if array flag set
        if not in_array:
            content_size = binary_read.read_uint32()  # contentSize
            binary_read.read_bytes(len(self.padding))
            logger.debug(
                f"content_size:{content_size} : called from offset:{binary_read.offset}"
            )
            if content_size == 1:
                binary_read.read_bytes(1)
                self.object_type = None
                self.value = None
                STRUCT_INDENT_COUNTER["object"] -= 1
                return
            end_pos = binary_read.offset + content_size
            self.object_type = binary_read.read_bytes(1)
            logger.debug(f"object_type:{self.object_type.hex()}")
            logger.info(
                f'{text_colours["Blue"]}ObjectProperty name:{self.name}, type:{object_types[self.object_type]} content_size:{content_size}, position:{binary_read.offset}'
            )
        # Set it to an array byte if array flag is set
        else:
            self.object_type = b"\x00"

        if self.object_type in [b"\x00"]:
            # num_objects_in_array = binary_read.read_uint32()

            # logger.debug(f"Array Object : {num_objects_in_array}")

            # for i in range(num_objects_in_array):
            object_array_type = binary_read.read_bytes(1)
            if object_array_type in [b"\x01"]:
                self.value = "Skipped object"

            elif object_array_type in [b"\x03"]:
                self.object_list = False
                self.value = self.ComponentType(binary_read)

            elif object_array_type in [b"\x07"]:
                self.value = "Skipped object"

            elif object_array_type in [b"\x09"]:
                self.value = self.NameType(binary_read)
                value = []
                prop = None

                length = self.find_extra_data_length(binary_read)
                logger.debug(length)
                self.extra_data = binary_read.read_bytes(length)

                logger.debug(f"{self.value}")
            else:
                logger.error(binary_read.peek(10, 20))
                raise Exception(f"object_array_type:{object_array_type}")

        elif self.object_type in [b"\x01"]:
            self.object_type = "Actor"
            object_data = binary_read.read_bytes(content_size - 1)
            self.value = "Skipped object"

        elif self.object_type in [b"\x03"]:

            self.object_list = True
            object_data = self.ComponentType(binary_read)

            self.value = object_data

        elif self.object_type in [b"\x07"]:
            self.object_type = "Not Sure"
            object_data = binary_read.read_bytes(content_size - 1)
            self.value = "Skipped object"

        elif self.object_type in [b"\x09"]:
            self.object_type = "Name"
            self.value = self.NameType(binary_read)

        else:
            logger.error(
                f"Unknown object type with byte:{self.object_type} @ position:{binary_read.offset}"
            )
            raise Exception(
                f"Unknown object type with byte:{self.object_type} @ position:{binary_read.offset}"
            )

        STRUCT_INDENT_COUNTER["object"] -= 1
        logger.info(
            f'{text_colours["Blue"]}Object Complete:{self.name}, {self.object_type}, {self.value}, {STRUCT_INDENT_COUNTER}'
        )

    def NameType(self, binary_read):
        value = binary_read.read_string()
        return value

    def ComponentType(self, binary_read):
        logger.debug(f"Starting ComponentType @ {binary_read.offset}")
        name = binary_read.read_string()
        logger.debug(f"name:{name}")
        script = binary_read.read_string()
        logger.debug(f"script:{script}")

        value = []
        prop = None
        while not isinstance(prop, NoneProperty):
            prop = binary_read.read_property()
            value.append(prop)
        extra_data = None
        if self.in_array:
            length = self.find_extra_data_length(binary_read)
            logger.debug(length)
            extra_data = binary_read.read_bytes(length)
            # logger.warning(f'extra_data:{extra_data}')
            # input('Enter')
        return {
            "name": name,
            "script": script,
            "value": value,
            "extra_data": extra_data,
        }

    def find_extra_data_length(self, binary_read):
        starting_position = binary_read.offset
        stream_end_position = len(binary_read.file_array_buffer)
        while binary_read.offset < stream_end_position:
            next_byte = binary_read.read_bytes(1, quiet=True)
            if next_byte == b"/":
                get_position = binary_read.offset
                identifier = binary_read.read_bytes(5, quiet=True)
                if identifier == b"Game/":
                    binary_read.offset = starting_position
                    return get_position - 6 - starting_position
                else:
                    binary_read.offset = get_position
            elif next_byte == b"\x05":
                get_position = binary_read.offset
                identifier = binary_read.read_bytes(8, quiet=True)
                if identifier == b"\x00\x00\x00None\x00":
                    binary_read.offset = starting_position
                    return get_position - starting_position - 1
                else:
                    binary_read.offset = get_position
        binary_read.offset = starting_position
        return stream_end_position - starting_position

    def __repr__(self):
        return "{}, {}, {}".format(self.name, self.type, self.value)


class Object_Property:
    padding = bytes([0x00, 0x00, 0x00, 0x00, 0x00])
    type = "ObjectProperty"

    def __init__(self, name, binary_read):
        logger.debug(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}"
        )
        self.type = "ObjectProperty"
        self.name = name
        # logger.debug(binary_read.peek(30))
        content_size = binary_read.read_uint32()  # contentSize
        logger.debug(
            f"content_size:{content_size} : called from offset:{binary_read.offset}"
        )
        binary_read.read_bytes(len(self.padding))
        self.position = binary_read.offset
        self.unknown_byte = binary_read.read_bytes(1)
        logger.debug(f"Ukbyte:{self.unknown_byte.hex()}")
        logger.critical(
            f"{self.type}    >> {self.unknown_byte.hex()} : {binary_read.offset}"
        )

        object_data = binary_read.read_bytes(content_size - 1)
        self.value = "Skipped object"

        logger.info(
            f"ObjectProperty:{self.name}, type:{self.type}, size:{content_size}, value:{self.value}"
        )

    def __repr__(self):
        return "{}, {}, {}".format(self.name, self.type, self.value)
