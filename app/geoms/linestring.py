from app.geoms.point import Point3
from app.geoms.curve import Curve
from app.geoms.utils.renderable import Renderable3d
from OpenGL import GL


class LineString(Curve, Renderable3d):

    def __init__(self, vertices=None, color=None):
        """renderable_vertex_array must be a list of Point objects"""

        Curve.__init__(self)
        Renderable3d.__init__(self, elements_type=GL.GL_LINES, color=color)

        if vertices is None:
            vertices = list()

        if not isinstance(vertices, list) or any(not isinstance(v, Point3) for v in vertices):
            raise TypeError("LineString.__init__ requires 'vertices' to be a list of Point3 objects.")

        self.vertices = vertices

        self.update_substructures()

    def update_substructures(self):
        self.update_bounding_box()
        self.update_renderable_arrays()

    def update_dcel(self):
        if len(self) == 1:
            self.dcel.make_from_points(*self.vertices)
        elif len(self) > 1:
            self.dcel.make_from_line(self)

    def update_bounding_box(self):
        if len(self) > 0:
            vertices = self.vertices
            the_min = Point3(vertices[0])
            the_max = Point3(vertices[0])

            for v in vertices:
                for i, coord in enumerate(v.tolist()):
                    the_min[i] = min(the_min[i], coord)
                    the_max[i] = max(the_max[i], coord)

            self.bounding_box.set_min(the_min)
            self.bounding_box.set_max(the_max)

    def add_vertex(self, v, i=None):
        if not isinstance(v, Point3):
            raise TypeError("Linestring.add_vertex requires parameter to be a Point3")

        if i is None:
            i = len(self.vertices)  # by default add the vertex as last vertex

        self.vertices.insert(i, v)
        self.update_substructures()

    def pop_vertex(self, i=-1):
        popped = self.vertices.pop(i)
        self.update_substructures()
        return popped

    def remove_vertex(self, i=-1):
        self.pop_vertex(i)

    def update_vertex(self, v, i=-1):
        """
        replace a vertex of this object
        :param v: the new Point3 to replace
        :param i: the vertex to be updated
        :return:
        """

        if not isinstance(v, Point3):
            raise TypeError("LineString.add_vertex requires parameter to be Point3")
        self.vertices[i] = v
        self.update_substructures()

    def is_valid(self):
        return isinstance(self.vertices, (list, tuple)) and len(self) > 1

    def wkt(self):
        """
        get a well-known text representation of this geometry
        :return:
        """
        return "LINESTRING({})".format(', '.join(["{} {} {}".format(v.x(), v.y(), v.z()) for v in self.vertices]))


    def __len__(self):
        return len(self.vertices)

    def __getitem__(self, i):
        return self.vertices[i]

    def __setitem__(self, i, value):
        self.vertices[i] = value

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, ', '.join(["{} {} {}".format(v.x(), v.y(), v.z()) for v in self.vertices]))

    def __hash__(self):
        """Allows for using a Geometry as a key of a set or a dictionary."""
        return hash(id(self))

    def __eq__(self, other):
        if len(self) != len(other):
            return False

        for i, v in enumerate(self.vertices):
            if v != other.vertices[i]:
                return False

        return True
