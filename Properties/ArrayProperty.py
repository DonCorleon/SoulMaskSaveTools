from config import *
import inspect
from .NoneProperty import NoneProperty
from .StructProperty import StructProperty
from.ObjectProperty import ObjectProperty

from .BoolProperty import BoolProperty
from .ByteProperty import ByteProperty
from .DoubleProperty import DoubleProperty
from .FloatProperty import FloatProperty
from .IntProperty import IntProperty
from .Int64Property import Int64Property
from .UInt32Property import UInt32Property

from .EnumProperty import EnumProperty
from .NameProperty import NameProperty
from .StrProperty import StrProperty
from .TextProperty import TextProperty


class ArrayProperty:
    padding = bytes([0x00, 0x00, 0x00, 0x00])
    unknown = bytes([0x00] * 17)
    type = "ArrayProperty"

    def __init__(self, name, binary_read):
        logger.debug(f'{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}')
        self.type = "ArrayProperty"
        self.name = name

        content_count = binary_read.read_uint32()
        logger.debug(f'content_count:{content_count} : called from offset:{binary_read.offset}')
        binary_read.read_bytes(4)

        self.subtype = binary_read.read_string()
        unknown_byte = binary_read.read_bytes(1).hex()

        logger.debug(f'Array subtype:{self.subtype}')

        if self.subtype in ['ObjectProperty']:
            self.value = ObjectProperty(self.name, binary_read, in_array=True)

        elif self.subtype in ['StructProperty']:
            logger.info(f'HERE')
            content_size = binary_read.read_int32()
            self.value = []
            prop = None
            while not isinstance(prop, NoneProperty):
                prop = binary_read.read_property()
                self.value.append(prop)
            '''
            struct_content_count = binary_read.read_uint32()
            logger.warning(f'struct_content_count:{struct_content_count}')
            struct_name = binary_read.read_string()
            logger.warning(f'struct_name:{struct_name}')
            struct_type = binary_read.read_string()
            logger.warning(f'struct_type:{struct_type}')
            unknown_int = binary_read.read_int32()
            binary_read.read_bytes(len(self.padding))

            self.value = []
            substruct_name = binary_read.read_string()  # Collection name
            binary_read.read_bytes(len(self.unknown))  # Adjust pointer after unknown bytes
            if substruct_name in ['Guid']:
                if struct_content_count > 1:
                    logger.warning(f'Found more than 1 guid')
                    self.value =[]
                    self.value.append([binary_read.read_uuid() for _ in range(struct_content_count)])
                else:
                    self.value = binary_read.read_uuid()

            else:

                for i in range(struct_content_count):
                    #logger.warning(f'Start Array StructProperty "{substruct_name}" : {binary_read.offset}')
                    substruct = []
                    while True:
                        subname = binary_read.read_string()  # Read property type
                        if subname[:4] == 'None':  # Stop at 'None'
                            break

                        if subname == 'EProficiency':
                            binary_read.read_bytes(1)
                            subtype = 'EProficiency'
                            substruct.append(binary_read.read_string())
                            continue

                        subtype = binary_read.read_string()  # Read property value type

                        if subtype == 'BoolProperty':
                            subvalue = BoolProperty(subname, binary_read)
                        elif subtype == 'StructProperty':
                            subvalue = StructProperty(subname, binary_read)
                        elif subtype == 'EnumProperty':
                            subvalue = EnumProperty(subname, binary_read)
                        elif subtype == 'IntProperty':
                            subvalue = IntProperty(subname, binary_read)
                        elif subtype == 'FloatProperty':
                            subvalue = FloatProperty(subname, binary_read)
                        elif subtype == 'DoubleProperty':
                            subvalue = DoubleProperty(subname, binary_read)
                        elif subtype == 'ByteProperty':
                            subvalue = binary_read.read_bytes(8)
                        elif subtype == 'TextProperty':
                            subvalue = TextProperty(subname, binary_read)
                        elif subtype == 'StructProperty':
                            subvalue = StructProperty(subname, binary_read)
                        elif subtype == 'ArrayProperty':
                            #logger.warning(f'Internal Array found {subname}')
                            subvalue = ArrayProperty(subname,binary_read)
                            logger.warning(f'Internal Array finished {subname}')
                        elif subtype == 'ObjectProperty':
                            subvalue = ObjectProperty(subname, binary_read)

                        else:
                            logger.warning(f'Unknown Array subtype:"{self.subtype}" | {self.subtype.encode().hex()}')
                            logger.warning(binary_read.read_string())
                            raise Exception(f'Unknown subtype:"{self.subtype}" | {self.subtype.encode().hex()}')
                        substruct.append({'name': subname, 'type': subtype, 'value': subvalue})
                    logger.debug(f'Iteration: {i}, Position: {binary_read.offset}, Subname: {subname}, Subtype: {subtype}')
                    self.value = [{substruct_name: substruct}]
        '''
        elif self.subtype in ['IntProperty']:
            #binary_read.read_bytes(1)
            int_content_count = binary_read.read_uint32()
            logger.warning(f'int_content_count:{int_content_count}')
            self.value = []
            for i in range(int_content_count):
                self.value.append(binary_read.read_int32())
            logger.warning(f'Array IntProperty >> name:{self.name}, type:{self.type}, subtype:{self.subtype}, value:{self.value}')
        else:
            logger.warning(f'Unknown Array subtype:"{self.subtype} | {self.subtype.hex()}"')
            raise Exception(f'Unknown subtype:"{self.subtype} | {self.subtype.hex()}"')


        logger.info(f'Array Complete:{self.value}')


    def __repr__(self):
        return '{}, {}, {}'.format(
            self.name,
            self.type,
            self.value)

        '''
        return
        content_size = binary_read.read_uint32()

        logger.warning(f'content_size:{content_size} : called from offset:{binary_read.offset}')
        binary_read.read_bytes(4)
        self.subtype = binary_read.read_string()
        unknown_byte = binary_read.read_bytes(1)

        #self.value = binary_read.read_bytes(content_size)
        #return

        self.generic_type = None
        #self.unknown_byte = binary_read.read_bytes(1)
        #logger.info(f'Ukbyte:{self.unknown_byte.hex()}')
        pos_start = binary_read.offset

        if self.subtype == "StructProperty":
            content_count = binary_read.read_uint32()
            logger.warning(f'content_count:{content_count} : called from offset:{binary_read.offset}')
            for _ in range(content_count):
                logger.info('New Entry')
                name_again = binary_read.read_string()
                #if name_again != self.name:
                #    raise Exception()
                subtype_again = binary_read.read_string()
                #if subtype_again != self.subtype:
                #    raise Exception()
                content_size = binary_read.read_uint32()  # arraySize
                binary_read.read_bytes(len(ArrayProperty.padding))
                self.generic_type = binary_read.read_string()
                unknown = binary_read.read_bytes(17)
                if unknown != ArrayProperty.unknown:
                    logger.critical(unknown)
                    raise Exception()
                self.value = []

                if self.generic_type == "Guid":
                    self.value.append(binary_read.read_uuid())
                else:
                    logger.critical(self.generic_type)
                    struct_element_instance = []
                    struct_element_instance_child_property = None
                    while not isinstance(struct_element_instance_child_property, NoneProperty):
                        struct_element_instance_child_property = binary_read.read_property()
                        struct_element_instance.append(struct_element_instance_child_property)
                    self.value.append(struct_element_instance)

            logger.critical(f'ArrayProperty:{self.name}, type:{self.type}, subtype:{self.subtype}, value:{self.value}')


        elif self.subtype in ["EnumProperty", "NameProperty", "StrProperty"]:
            # Read the number of ObjectProperty elements in the array
            content_count = binary_read.read_uint32()
            self.value = [binary_read.read_string() for _ in range(content_count)]

            logger.critical(f'ArrayProperty:{self.name}, type:{self.type}, subtype:{self.subtype}, value:{self.value}')

        elif self.subtype in ["ObjectProperty"]:
            self.value = binary_read.read_bytes(content_size)
            logger.info(f'Skipping Array element of ObjectProperty')
            return
            logger.debug(binary_read.peek(30))
            content_count = binary_read.read_uint32()
            #logger.debug(f'content_count:{content_count} : called from offset:{binary_read.offset}')
            self.unknown_byte = binary_read.read_bytes(1)
            #logger.info(f'Ukbyte:{self.unknown_byte.hex()}')
            self.value =[]
            for _ in range(content_count):
                self.value.append(binary_read.read_string())
            logger.critical(f'Array unknown byte : {binary_read.read_bytes(1)}')

            #binary_read.offset -= 1
        '''
        '''
            logger.debug(f'content_size:{content_size} : called from offset:{binary_read.offset}')
            binary_read.read_bytes(len(self.padding))
            
            # Read the number of ObjectProperty elements in the array
            content_count = binary_read.read_uint32()
            self.value = [binary_read.read_string() for _ in range(content_count)]


            logger.debug(f'content_size:{content_size} : called from offset:{binary_read.offset}')

            self.value = binary_read.read_bytes(content_size)
            #logger.info(f'Array data bypassed for type ObjectProperty')
            object_data = binary_read.new_reader(self.value)
            #logger.warning(f'{self.value[:50].hex(" ",1)}')
            num_array_objects = object_data.read_int32()
            logger.debug(f'Array contains {num_array_objects} objects')
            unknown_byte = object_data.read_bytes(1)
            object_name = object_data.read_string()
            logger.warning(f'New objects name : {object_name}')
            object_subname = object_data.read_string()
            logger.warning(f'New objects subname : {object_subname}')
            object_data.deserialize(has_header=False)
            #binary_read.offset = binary_read.offset -1
        '''
        '''
        else:
            logger.debug(f'ArrayProperty, Unknown subtype: {self.subtype}')
            self.value = binary_read.read_bytes(content_size)
            logger.critical(f'Position:{binary_read.offset}, {self.name}, {self.type}, {self.subtype}, {pos_start}:{binary_read.offset}, {content_size}:{binary_read.offset-pos_start}')

        logger.critical(f'ArrayProperty:{self.name}, type:{self.type}, subtype:{self.subtype}, generictype:{self.generic_type}, value:{self.value}')
        '''
