from app.geoms.solid import Solid

import numpy as np


class Tetrahedron(Solid):

    def __init__(self, color=None):
        Solid.__init__(self, color=color)

        self.renderable_vertex_array = \
            np.zeros(4,
                     [
                         ('coords', [
                             ('x', np.float32),
                             ('y', np.float32),
                             ('z', np.float32)
                             ]),
                         ('color', [
                             ('r', np.float32),
                             ('g', np.float32),
                             ('b', np.float32),
                             ('a', np.float32)
                             ])
                         # if needed, normals can be added here
                         ]
                     )

        self.renderable_vertex_array["coords"] = [
            # coordinates of a tetrahedron of radius 1 centered in the origin
            (0.000, 0.000, 1.000),
            (0.943, 0.000, -0.333),
            (-0.471, 0.816, -0.333),
            (-0.471, -0.816, -0.333)
            ]

        # rainbow coloring (each vertex a different color)
        self.renderable_vertex_array["color"] = [
            tuple(self.color.get_rgba()),  # front-top-right
            tuple(self.color.get_rgba()),  # front-top-left
            tuple(self.color.get_rgba()),  # front-bottom-left
            tuple(self.color.get_rgba())  # front-bottom-right
            ]

        self.renderable_element_array = np.array([
            0, 1, 2,
            3, 2, 1,
            0, 2, 3,
            0, 3, 1
            ], dtype=np.uint32)

        self.renderable_outline_element_array = np.array([
            0, 1, 0, 2, 0, 3,  # all edges going from top vertex to the base
            1, 2, 2, 3, 3, 1  # the base of the tetrahedron
            ], dtype=np.uint32)


    def volume(self):
        return Tetrahedron.signed_volume(*self._vertices)


    @staticmethod
    def signed_volume(a, b, c, d):
        """
        :param a: Vector3
        :param b: Vector3
        :param c: Vector3
        :param d: Vector3
        :return: the volume (with sign) of the tetrahedron formed by the given points
        """

        from app.utils.vector import Vector3
        if not all(isinstance(p, Vector3) for p in [a, b, c, d]):
            raise TypeError("Tetrahedron.signed_volume requires all parameters to be Vector3 objects")

        return (
                (a.x() - d.x()) * (b.y() - d.y()) * (c.z() - d.z()) +
                (a.y() - d.y()) * (b.z() - d.z()) * (c.x() - d.x()) +
                (a.z() - d.z()) * (b.x() - d.x()) * (c.y() - d.y()) -
                (a.z() - d.z()) * (b.y() - d.y()) * (c.x() - d.x()) -
                (b.z() - d.z()) * (c.y() - d.y()) * (a.x() - d.x()) -
                (c.z() - d.z()) * (a.y() - d.y()) * (b.x() - d.x())
        )
