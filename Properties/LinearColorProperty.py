from config import *
import inspect


class LinearColorProperty:
    def __init__(self, binary_data):
        self.type = None
        r = binary_data.read_float32()
        g = binary_data.read_float32()
        b = binary_data.read_float32()
        a = binary_data.read_float32()
        self.value = {'r': r, 'g': g, 'b': b, 'a': a}
    def __repr__(self):
         return str(self.value)
