from abc import abstractmethod
from app.geoms.geometry import Geometry


class Surface(Geometry):
    """
    This should be an abstract class(see Geometry class).
    Since Surface inherits from Geometry, which is abstract, Surface is also abstract
    If we would want make this class NOT abstract, we should override the abstract methods in Geometry
    """


    @abstractmethod
    def __init__(self):
        Geometry.__init__(self)


    @abstractmethod
    def wkt(self):
        pass
