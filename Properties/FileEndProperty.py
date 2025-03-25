from config import *
import inspect
from .NoneProperty import NoneProperty


class FileEndProperty:
    def __init__(self):
        logger.debug(
            f"{self.__class__.__name__}.{inspect.currentframe().f_code.co_name}"
        )
        self.type = "FileEndProperty"

    bytes = NoneProperty.bytes + bytes([0x00, 0x00, 0x00, 0x00])
    type = "FileEndProperty"
