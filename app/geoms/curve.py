from abc import abstractmethod
from app.geoms.geometry import Geometry


class Curve(Geometry):
    """
    This should be an abstract class(see Geometry class).
    Since Curve inherits from Geometry, which is abstract, Curve is also abstract
    If we would want make this class NOT abstract, we should override the abstract methods in Geometry
    """
    @abstractmethod
    def __init__(self):
        Geometry.__init__(self)
        pass


    @abstractmethod
    def wkt(self):
        pass
