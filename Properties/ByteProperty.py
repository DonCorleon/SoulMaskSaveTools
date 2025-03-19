from config import *
import inspect


class ByteProperty:
    padding = bytes([0x00, 0x00, 0x00, 0x00])
    unknown = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    type = "ByteProperty"

    def __init__(self, name, binary_read):
        logger.debug(f'{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}')
        self.type = "ByteProperty"
        self.name = name
        content_size = binary_read.read_uint32()
        binary_read.read_bytes(4)
        self.subtype = binary_read.read_string()

        binary_read.read_bytes(1)

        if self.subtype == "StructProperty":
            content_count = binary_read.read_uint32()
            name_again = binary_read.read_string()
            if name_again != self.name:
                raise Exception()
            subtype_again = binary_read.read_string()
            if subtype_again != self.subtype:
                raise Exception()
            binary_read.read_uint32()
            binary_read.read_bytes(len(ByteProperty.padding))
            self.generic_type = binary_read.read_string()
            unknown = binary_read.read_bytes(17)
            if unknown != ByteProperty.unknown:
                raise Exception()
            self.value = []
            if self.generic_type == "Guid":
                for _ in range(content_count):
                    self.value.append(binary_read.read_bytes(16))
            else:
                for _ in range(content_count):
                    struct_element_instance = []
                    struct_element_instance_child_property = None
                    while not isinstance(struct_element_instance_child_property, NoneProperty):
                        struct_element_instance_child_property = binary_read.read_property()
                        struct_element_instance.append(struct_element_instance_child_property)
                    self.value.append(struct_element_instance)
        else:
            self.value = int.from_bytes(binary_read.read_bytes(content_size), 'big')

    def __repr__(self):
        return '{}, {}, {}, {}'.format(
            self.name,
            self.type,
            self.subtype,
            self.value)
