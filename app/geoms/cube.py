from app.geoms.solid import Solid
import numpy as np


class Cube(Solid):

    def __init__(self, color=None):
        Solid.__init__(self, color=color)

        self.renderable_vertex_array = \
            np.zeros(8,
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
            # coordinates of a cube with edge-length 1 centered in the origin
            (-0.5, -0.5, +0.5),  # left-bottom-front
            (+0.5, -0.5, +0.5),  # right-bottom-front
            (+0.5, +0.5, +0.5),  # right-top-front
            (-0.5, +0.5, +0.5),  # left-top-front
            (-0.5, -0.5, -0.5),  # left-bottom-back
            (+0.5, -0.5, -0.5),  # right-bottom-back
            (+0.5, +0.5, -0.5),  # right-top-back
            (-0.5, +0.5, -0.5),  # left-top-back
        ]

        # rainbow coloring (each vertex a different color)
        self.renderable_vertex_array["color"] = [
            tuple(self.color.get_rgba()),  # left-bottom-front
            tuple(self.color.get_rgba()),  # right-bottom-front
            tuple(self.color.get_rgba()),  # right-top-front
            tuple(self.color.get_rgba()),  # left-top-front
            tuple(self.color.get_rgba()),  # left-bottom-back
            tuple(self.color.get_rgba()),  # right-bottom-back
            tuple(self.color.get_rgba()),  # right-top-back
            tuple(self.color.get_rgba())   # left-top-back
        ]

        self.renderable_element_array = np.array([
            0, 1, 2,    2, 3, 0,  # front face
            1, 5, 6,    6, 2, 1,  # right face
            5, 4, 7,    7, 6, 5,  # back face
            3, 2, 6,    6, 7, 3,  # top face
            4, 0, 3,    3, 7, 4,  # left face
            4, 5, 1,    1, 0, 4   # bottom face
        ], dtype=np.uint32)

        self.renderable_outline_element_array = np.array([
            0, 1,   1, 2,   2, 3,   3, 0,  # front face
            4, 5,   5, 6,   6, 7,   7, 4,  # back face
            0, 4,   1, 5,   2, 6,   3, 7   # edges connecting back and front faces
        ], dtype=np.uint32)