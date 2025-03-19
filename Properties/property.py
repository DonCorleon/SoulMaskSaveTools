
'''
from .Property import

        elif property_type == "MulticastInlineDelegateProperty":
            value = MulticastInlineDelegateProperty(property_name, self)



class MulticastInlineDelegateProperty:
    padding = bytes([0x00, 0x00, 0x00, 0x00, 0x00])
    unknown = bytes([0x01, 0x00, 0x00, 0x00])
    type = "MulticastInlineDelegateProperty"

    def __init__(self, name, binary_read):
        logger.debug(f'{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}')
        self.name = name
        self.type = "MulticastInlineDelegateProperty"
        binary_read.read_uint32()  # contentSize
        binary_read.read_bytes(len(MulticastInlineDelegateProperty.padding))
        binary_read.read_bytes(len(MulticastInlineDelegateProperty.unknown))
        self.object_name = binary_read.read_string()
        self.function_name = binary_read.read_string()
        logger.debug(f'Position:{binary_read.offset}, {self.name}, {self.type}')

    def __repr__(self):
        return '{}, {}, {}, {}'.format(
            self.name,
            self.type,
            self.object_name,
            self.function_name)


class IntProperty:
    def __init__(self, data):
        self.name = None
        self.data = data
        self.data_size = len(self.data)
    def __repr__(self):
        if self.data:
            return '{}, {}, {}'.format(
            self.name,
            self.data_size,
            'Seralized Byte Data')
'''
