from app.geoms.linestring import LineString
from app.geoms.point import Point3


class LinearRing(LineString):
    def __init__(self, vertices=None, color=None):
        """renderable_vertex_array must be a list of Point objects"""

        LineString.__init__(self, vertices=vertices, color=color)

        if self.is_open():
            self.close()


    def __len__(self):
        return len(self.vertices) if self.is_open() else len(self.vertices) - 1


    def __setitem__(self, key, value):
        self.open()
        self.vertices[key] = value
        self.close()


    def __getitem__(self, i):
        self.open()
        the_item = self.vertices[i]
        self.close()
        return the_item


    def pop_vertex(self, i=-1):
        self.open()
        popped = self.vertices.pop(i)
        self.close()
        self.update_substructures()
        return popped


    def update_vertex(self, v, i=-1):
        """
        replace a vertex of this object
        :param v: the new BasePoint to replace
        :param i: the vertex to be updated
        :return:
        """
        if not isinstance(v, Point3):
            raise TypeError("LinearRing.update_vertex requires parameter to be Point3")

        self.open()
        LineString.update_vertex(self, v, i)
        self.close()


    def add_vertex(self, v, i=None):
        if not isinstance(v, Point3):
            raise TypeError("LinearRing.add_vertex requires parameter to be a Point3")

        self.open()
        LineString.add_vertex(self, v, i)
        self.close()


    def is_open(self):
        return not self.is_closed()


    def is_closed(self):
        """
        check if the line is closed. Only true when the last vertex IS also the first (if the last and first vertex
        have same coordinates but are two different objects it still means that the line is open)
        :return:
        """
        if not self.vertices or len(self.vertices) in (0, 1):
            return False
        else:
            return self.vertices[0] is self.vertices[-1]


    def open(self):
        """
        if the line is closed, open it
        :return:
        """
        if self.is_closed():
            # print("open")
            del self.vertices[-1]
            self.update_substructures()


    def close(self):
        """
        if the line is open and can be closed (has at least 3 vertices), close it
        :return:
        """
        if len(self) >= 3 and self.is_open():
            # print("close")
            self.vertices.append(self.vertices[0])
            self.update_substructures()


    def is_valid(self):
        return isinstance(self.vertices, (list, tuple)) and len(self) > 2
