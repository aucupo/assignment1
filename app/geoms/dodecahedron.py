from app.geoms.solid import Solid
import numpy as np


class Dodecahedron(Solid):

    def __init__(self, color=None):
        Solid.__init__(self, color=color)

        self.renderable_vertex_array = \
            np.zeros(20,
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

        phi = (1 + (5 ** (1/2))) / 2

        self.renderable_vertex_array["coords"] = [
            # coordinates of a cube with edge-length 1 centered in the origin
            (+1.0, +1.0, +1.0),
            (+1.0, +1.0, -1.0),
            (+1.0, -1.0, +1.0),
            (+1.0, -1.0, -1.0),
            (-1.0, +1.0, +1.0),
            (-1.0, +1.0, -1.0),
            (-1.0, -1.0, +1.0),
            (-1.0, -1.0, -1.0),
            (0.0, +1.0 / phi, +phi),
            (0.0, +1.0 / phi, -phi),
            (0.0, -1.0 / phi, +phi),
            (0.0, -1.0 / phi, -phi),
            (+1.0 / phi, +phi, 0.0),
            (+1.0 / phi, -phi, 0.0),
            (-1.0 / phi, +phi, 0.0),
            (-1.0 / phi, -phi, 0.0),
            (+phi, 0.0, +1 / phi),
            (+phi, 0.0, -1 / phi),
            (-phi, 0.0, +1 / phi),
            (-phi, 0.0, -1 / phi)
        ]

        phi = (1 + (5 ** (1 / 2))) / 2

        # points = [
        #     Point3(+1.0, +1.0, +1.0, color=Color(1, 0, 0)),  # 0
        #     Point3(+1.0, +1.0, -1.0, color=Color(0, 0, 0)),  # 1
        #     Point3(+1.0, -1.0, +1.0, color=Color(0, 0, 1)),  # 2
        #     Point3(+1.0, -1.0, -1.0, color=Color(0, 0, 0)),  # 3
        #     Point3(-1.0, +1.0, +1.0, color=Color(0, 0, 0)),  # 4
        #     Point3(-1.0, +1.0, -1.0, color=Color(0, 0, 0)),  # 5
        #     Point3(-1.0, -1.0, +1.0, color=Color(0, 0, 0)),  # 6
        #     Point3(-1.0, -1.0, -1.0, color=Color(0, 0, 0)),  # 7
        #     Point3(0.0, +1.0 / phi, +phi, color=Color(0, 1, 0)),  # 8
        #     Point3(0.0, +1.0 / phi, -phi, color=Color(0, 0, 0)),  # 9
        #     Point3(0.0, -1.0 / phi, +phi, color=Color(0, 1, 1)),  # 10
        #     Point3(0.0, -1.0 / phi, -phi, color=Color(0, 0, 0)),  # 11
        #     Point3(+1.0 / phi, +phi, 0.0, color=Color(0, 0, 0)),  # 12
        #     Point3(+1.0 / phi, -phi, 0.0, color=Color(0, 0, 0)),  # 13
        #     Point3(-1.0 / phi, +phi, 0.0, color=Color(0, 0, 0)),  # 14
        #     Point3(-1.0 / phi, -phi, 0.0, color=Color(0, 0, 0)),  # 15
        #     Point3(+phi, 0.0, +1 / phi, color=Color(1, 1, 0)),  # 16
        #     Point3(+phi, 0.0, -1 / phi, color=Color(0, 0, 0)),  # 17
        #     Point3(-phi, 0.0, +1 / phi, color=Color(0, 0, 0)),  # 18
        #     Point3(-phi, 0.0, -1 / phi, color=Color(0, 0, 0))  # 19
        # ]

        # rainbow coloring (each vertex a different color)
        self.renderable_vertex_array["color"] = [
            tuple(self.color.get_rgba()),
            tuple(self.color.get_rgba()),
            tuple(self.color.get_rgba()),
            tuple(self.color.get_rgba()),
            tuple(self.color.get_rgba()),
            tuple(self.color.get_rgba()),
            tuple(self.color.get_rgba()),
            tuple(self.color.get_rgba()),
            tuple(self.color.get_rgba()),
            tuple(self.color.get_rgba()),
            tuple(self.color.get_rgba()),
            tuple(self.color.get_rgba()),
            tuple(self.color.get_rgba()),
            tuple(self.color.get_rgba()),
            tuple(self.color.get_rgba()),
            tuple(self.color.get_rgba()),
            tuple(self.color.get_rgba()),
            tuple(self.color.get_rgba()),
            tuple(self.color.get_rgba()),
            tuple(self.color.get_rgba())
        ]

        self.renderable_element_array = np.array([
            #TODO compute the faces!
        ], dtype=np.uint32)

        self.renderable_outline_element_array = np.array([
            # TODO compute the edges!
        ], dtype=np.uint32)