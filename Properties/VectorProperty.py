from config import *
import inspect


class VectorProperty:
    def __init__(self, binary_data):
        logger.debug(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name} << {inspect.stack()[1].function} << {inspect.stack()[2].function}"
        )
        x = binary_data.read_float32()
        y = binary_data.read_float32()
        z = binary_data.read_float32()
        self.value = {"x": x, "y": y, "z": z}

    def __repr__(self):
        return str(self.value)
