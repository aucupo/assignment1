from app.geoms.utils.transformable import Transformable
from PyQt4.QtGui import QVector3D


# TODO: not necessary to inherit from Movable. If this creates problems remove inheritance
class Box3D(Transformable):
    def __init__(self, the_min=None, the_max=None):
        Transformable.__init__(self)

        from app.geoms.point import Vector3

        self._min = the_min if isinstance(the_min, Vector3) else Vector3(0, 0, 0)
        self._max = the_max if isinstance(the_max, Vector3) else Vector3(0, 0, 0)

    def min(self):
        return self._min

    def max(self):
        return self._max

    def set_min(self, the_min):
        self._min = the_min

    def set_max(self, the_max):
        self._max = the_max

    def get_x_length(self):
        return (self._max - self._min).x()

    def get_y_length(self):
        return (self._max - self._min).y()

    def get_z_length(self):
        return (self._max - self._min).z()

    def apply_transformation(self):
        min_vec = QVector3D(self._min.x(), self._min.y(), self._min.z())
        max_vec = QVector3D(self._max.x(), self._max.y(), self._max.z())

        min_vec = self._model2world_matrix * min_vec
        max_vec = self._model2world_matrix * max_vec

        from app.geoms.point import Vector3

        self._min = Vector3(min_vec.x(), min_vec.y(), min_vec.z())
        self._max = Vector3(max_vec.x(), max_vec.y(), max_vec.z())