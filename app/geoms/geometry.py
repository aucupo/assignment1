from app.geoms.utils.box import Box3D
from abc import ABCMeta, abstractmethod


# Python 2 syntax for abstract class
# class Geometry:
#     __metaclass__ = ABCMeta

# Python 3 syntax for abstract class (if using python 2 replace the line below with the two above)
class Geometry(object, metaclass=ABCMeta):
    """
    Base geometry class. All other geometries inherits from this
    """

    def __init__(self, *args, **kwargs):
        # print("Geometry.__init__")

        self.bounding_box = kwargs.pop('bounding_box', Box3D())

    @abstractmethod
    def update_bounding_box(self):
        """this method must be reimplemented in derived classes"""
        pass

    @abstractmethod
    def is_valid(self):
        pass

    # __hash__ is a special magic function. It is not inherited by subclasses unless certain things
    #  happen (see here: https://docs.python.org/2/reference/datamodel.html), so let's make it abstract to
    # force its reimplementation in subclasses
    @abstractmethod
    def __hash__(self):
        """Allows for using a Geometry as a key of a set or a dictionary."""
        return hash(id(self))
