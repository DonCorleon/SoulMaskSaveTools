from config import *
import inspect


class GuidProperty:
    type = "GuidProperty"

    def __init__(self, name, binary_read, length):
        logger.debug(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}"
        )
        self.type = "GuidProperty"
        self.name = name

        if length > 16:
            logger.warning(f"Found more than 1 guid")
            self.value = []
            self.value.append([binary_read.read_uuid() for _ in range(length // 16)])
        elif length == 16:
            self.value = binary_read.read_uuid()
        else:
            self.value = None
            # raise Exception(f'Error with GUID length')

        if self.value == "00000000-0000-0000-0000-000000000000":
            logger.error(binary_read.peek(20, 20))
            raise Exception(f"GuidProperty read incorrectly")
        logger.debug(f"GuidProperty:{self.name}, type:{self.type}, value:{self.value}")

    def __repr__(self):
        return "{}, {}, {}".format(self.name, self.type, self.value)
