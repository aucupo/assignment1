import random as rand
import numpy as np


class Color(object):
    def __init__(self, *args, **kwargs):
        # NOTE: there is not control on the values of the passed parameters
        self.r = rand.uniform(0.0, 1.0)  # default to random
        self.g = rand.uniform(0.0, 1.0)  # default to random
        self.b = rand.uniform(0.0, 1.0)  # default to random
        self.a = 1.0  # default to fully opaque (0: transparent)

        if len(args) == 1:
            if isinstance(args[0], float):
                self.r = self.g = self.b = args[0]
        elif len(args) >= 3:
            self.r = args[0]
            self.g = args[1]
            self.b = args[2]

        if all(rgb in kwargs for rgb in ("r", "g", "b")):
            self.r = kwargs['r']
            self.g = kwargs['g']
            self.b = kwargs['b']

    def get_rgba(self):
        return [self.r, self.g, self.b, self.a]
