from app.geoms.point import Point3
from app.geoms.linearring import LinearRing
from app.geoms.line import Line
from app.geoms.surface import Surface
from app.geoms.utils.renderable import Renderable3d
from app.utils.color import Color

from OpenGL import GL


class Polygon(Surface, Renderable3d):
    def __init__(self, rings=None, color=None):

        if rings is None:
            rings = [LinearRing(color=Color(0, 0, 0))]

        if not isinstance(rings, list) or any(not isinstance(r, LinearRing) for r in rings):
            raise TypeError("Polygon.__init__ requires 'rings' to be a list of LinearRing objects.")

        Surface.__init__(self)
        Renderable3d.__init__(self, elements_type=GL.GL_TRIANGLES, color=color)

        # all rings should be black
        for r in rings:
            r.set_color(color=Color(0, 0, 0))

        self.rings = rings

        self.make_valid()

        self.update_substructures()

    @property
    def boundary(self):
        return self[0]

    @boundary.setter
    def boundary(self, val):
        self[0] = val

    @property
    def holes(self):
        return self[1:]

    @holes.setter
    def holes(self, val):
        if isinstance(val, LinearRing):
            val = [val]

        if not isinstance(val, list):
            raise TypeError("Polygon.holes: passed value should be either a "
                            "LinearRing or a list of LinearRing objects.")

        self.rings = self[0] + val

    def __setitem__(self, i, value):
        self.rings[i] = value

    def __getitem__(self, item):
        return self.rings[item]

    def update_substructures(self):
        self.update_bounding_box()
        self.update_renderable_arrays()

    def update_bounding_box(self):
        self.boundary.update_substructures()

    def render(self, shader_program):
        Renderable3d.render(self, shader_program=shader_program)
        self.boundary.render(shader_program=shader_program)

    def update_dcel(self):
        self.dcel.make_from_polygon(self)

    def add_vertex(self, v, i=None, ring=0):
        """
        add a vertex at the end of either the boundary (ring=0) or one of its holes (ring>0)
        :param v: the vertex (Point3) to be added
        :param i: the index where the vertex will be added (if None, at the end)
        :param ring: indicates to which ring of the polygon add the vertex
        :return:
        """
        if not isinstance(v, Point3):
            raise TypeError("Polygon.add_vertex requires parameter to be Point3")
        self[ring].add_vertex(v, i)
        self.update_substructures()

    def remove_vertex(self, i=-1, ring=-1):
        """
        remove the i-th vertex from the boundary (element=0) or from one of its holes (element>0)
        :param i: the vertex to remove
        :param ring: the element of the polygon from where the vertex is removed
        :return:
        """
        self[ring].remove_vertex(i)
        self.update_substructures()

    def update_vertex(self, v, i=-1, ring=0):
        """
        replace the last vertex of either the boundary (element=0) or of one of the holes (element>0)
        :param v: the new BasePoint to replace
        :param i: the index of the vertex to be updated
        :param ring: the element of the polygon to be updated
        :return:
        """

        if not isinstance(v, Point3):
            raise TypeError("Polygon.add_vertex requires parameter to be Point3")
        self[ring].update_vertex(v, i)
        self.update_substructures()

    def make_valid(self):
        # TODO: implement a function that checks that
        # the boundary renderable_vertex_array are in CCW order and that the
        # holes' renderable_vertex_array are in CW order
        # if not they are reordered correctly
        pass

    def contains_point_convex(self, a_point):

        for i, v_i in enumerate(self.boundary):
            edge = Line([self.boundary[i - 1], v_i])

            if edge.point_position(a_point) != 1:
                return False

        return True

    def contains_point(self, a_point):
        boundary = list(self.boundary)
        boundary = boundary[1:]
        is_in = False

        ray = Line([Point3(a_point.x(), a_point.y()), Point3(a_point.x(), a_point.y())])

        for i, v_i in enumerate(boundary):
            curr_edge = Line([boundary[i - 1], boundary[i]])

            x_max = max(curr_edge.start.x(), curr_edge.end.x())
            if x_max > a_point.x():
                ray.end.set_x(x_max + 1)

            if ray.intersects(curr_edge):
                is_in = not is_in

        return is_in

    def __eq__(self, other):
        # assume:
        #  - only convex polygons with vertices in counterclockwise order and
        #  - objects do not have multiple coinciding vertices

        if len(self) != len(other):
            return False

        offset = -1
        for i, v in enumerate(other.boundary.vertices):
            if self.boundary[0] == v:
                offset = i
                break

        if offset == -1:
            return False

        for i, v in enumerate(self.boundary.vertices):
            if v != other.boundary[(i + offset) % len(other)]:
                return False

        return True

    def __len__(self):
        """
        :return: the number of vertices of the boundary
        """
        return len(self.boundary)

    def __str__(self):
        # TODO as exercise make this function a 1-liner
        ring_wkt_list = list()
        for r in self.rings:
            r_wkt_str = "({})".format(', '.join(["{} {} {}".format(v.x(), v.y(), v.z()) for v in r.vertices]))
            ring_wkt_list.append(r_wkt_str)

        wkt_str = ', '.join(ring_wkt_list)

        return "{}({})".format(self.__class__.__name__, wkt_str)

    def wkt(self):
        """
        :return: a well-known text representation of this geometry
        """
        # TODO as exercise make this function a 1-liner

        ring_wkt_list = list()
        for r in self.rings:
            r_wkt_str = "({})".format(', '.join(["{} {} {}".format(v.x(), v.y(), v.z()) for v in r.vertices]))
            ring_wkt_list.append(r_wkt_str)

        wkt_str = ', '.join(ring_wkt_list)

        return "POLYGON({})".format(wkt_str)

    def is_valid(self):
        """
        :return: true, if the polygon is valid
        """
        # TODO: check that the boundary does not self-intersect + other meaningful checks
        return len(self.boundary) > 2  # a polygon must consists of at least a boundary with 3 edges

    def __hash__(self):
        """Allows for using a Vertex as a key of a set or a dictionary."""
        return hash(id(self))
