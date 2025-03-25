from config import *
import inspect


class SetProperty:
    padding = bytes([0x00, 0x00, 0x00, 0x00])
    type = "SetProperty"

    def __init__(self, name, binary_read):
        logger.debug(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}"
        )
        self.name = name
        self.type = "SetProperty"
        content_size = binary_read.read_uint32()
        binary_read.read_bytes(len(SetProperty.padding))
        self.subtype = binary_read.read_string()
        binary_read.read_bytes(1)

        if self.subtype == "StructProperty":
            binary_read.read_bytes(len(SetProperty.padding))
            content_count = binary_read.read_uint32()
            self.value = (
                []
            )  # [binary_read.read_property() for _ in range(content_count)]
            for _ in range(content_count):
                struct_element_instance = []
                struct_element_instance_child_property = None
                while not isinstance(
                    struct_element_instance_child_property, NoneProperty
                ):
                    struct_element_instance_child_property = binary_read.read_property()
                    struct_element_instance.append(
                        struct_element_instance_child_property
                    )
                self.value.append(struct_element_instance)
        elif self.subtype == "NameProperty":
            binary_read.read_bytes(4)
            content_count = binary_read.read_uint32()
            self.value = [binary_read.read_string() for _ in range(content_count)]
        else:
            self.value = binary_read.read_bytes(content_size)
        logger.debug(
            f"Position:{binary_read.offset}, {self.name}, {self.type}, {self.subtype}, {self.value}"
        )

    def __repr__(self):
        return "{}, {}, {}, {}".format(self.name, self.type, self.subtype, self.value)
