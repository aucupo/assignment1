from PyQt4.QtGui import QMatrix4x4
from PyQt4.QtGui import QVector3D
from app.utils.coords_conversion import *
from abc import ABCMeta, abstractmethod

# Python 2 syntax for abstract class
# class Transformable:
#     __metaclass__ = ABCMeta


# Python 3 syntax for abstract class (if using python 2 replace the line below with the two above)
class Transformable(object, metaclass=ABCMeta):

    def __init__(self, *args, **kwargs):
        # print("Movable3d.__init__")

        # TODO: replace Qt with numpy
        self._model2world_matrix = kwargs.pop('model2world_matrix', QMatrix4x4())

    def translate(self, x, y, z):
        """
        translate produces a translation by (x, y, z) .
        :param x: x coordinate of a translation vector.
        :param y: y coordinate of a translation vector.
        :param z: z coordinate of a translation vector.
        :return:
        """

        self._model2world_matrix.translate(x, y, z)

    def rotate(self, angle, x_component, y_component, z_component):
        """
        rotate produces a rotation of angle degrees around the vector (x, y, z).
        :param angle: the angle of rotation, in degrees.
        :param x_component: x coordinate of a vector
        :param y_component: y coordinate of a vector
        :param z_component: z coordinate of a vector
        :return:
        """

        self._model2world_matrix.rotate(angle, x_component, y_component, z_component)

    def scale(self, x, y=None, z=None):
        """
        scale produces a non uniform scaling along the x, y, and z axes. The three
        parameters indicate the desired scale factor along each of the three axes.
        :param x: scale factor along the x-axis
        :param y: scale factor along the y-axis
        :param z: scale factor along the z-axis
        :return:
        """

        if y is None:
            y = z = x
        self._model2world_matrix.scale(x, y, z)

    def move(self, delta_x=0, delta_y=0, delta_z=0):
        self.translate(delta_x, delta_y, delta_z)

    def move_spherical(self, delta_theta=0, delta_phi=0, delta_radius=0):
        delta_x, delta_y, delta_z = spherical2cartesian(delta_theta, delta_phi, delta_radius)
        self.move(delta_x, delta_y, delta_z)

    def set_position(self, x, y, z):
        self.reset()  # reset the _model2world_matrix

        # now the object is located at the origin.
        # move it to the given x, y, z
        self.move(x, y, z)

    def set_position_spherical(self, theta, phi, radius):
        # transform the spherical coordinates to cartesian coordinates
        x, y, z = spherical2cartesian(theta, phi, radius)

        # set the cartesian position
        self.set_position(x, y, z)

    def reset(self):
        # reset the _model2world_matrix
        self._model2world_matrix.setToIdentity()

    @abstractmethod
    def apply_transformation(self):
        pass

    def world_coords(self):
        return self._model2world_matrix * QVector3D(0.0, 0.0, 0.0)

    @property
    def position(self):
        return self.world_coords()
