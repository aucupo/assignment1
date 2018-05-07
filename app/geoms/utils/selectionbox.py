from app.geoms.point import Point3
from app.geoms.linearring import LinearRing
from app.utils.color import Color


class SelectionBox:

    def __init__(self, c1=None, c2=None):

        if c1 is None:
            c1 = Point3(0, 0, 0)

        if c2 is None:
            # corner2 = corner1
            #  not a good choice because we would only have only
            # 1 Point referred by two different names

            # this is the way to go
            c2 = Point3(c1)

        assert isinstance(c1, Point3)
        assert isinstance(c2, Point3)

        self.corner1 = c1
        self.corner2 = c2
        self.boundary = LinearRing

        self.set_boundary()

    def set_boundary(self):
        v1 = Point3(self.corner1)
        v2 = Point3(self.corner2.x(), self.corner1.y(), 0)
        v3 = Point3(self.corner2)
        v4 = Point3(self.corner1.x(), self.corner2.y(), 0)

        self.boundary = LinearRing(vertices=[v1, v2, v3, v4, v1],
                                   color=Color(0, 0, 0))

    def move_corner2(self, delta=None):
        if delta is None:
            delta = Point3(0, 0, 0)

        assert isinstance(delta, Point3)
        self.corner2 += delta

        self.set_boundary()

    def render(self, shader_program):
        self.boundary.render(shader_program)

    def get_classical_bbox(self):
        """
        this class is defined in a way that corner1 and corner2 may represent
        one of the following cases
        c2-------|--------c2
        |        |        |
        |    2   |    1   |
        |        |        |
        |--------c1-------|
        |        |        |
        |   3    |    4   |
        |        |        |
        c2-------|--------c2

        computes a "classical" bounding box: bottom-left and top-right corners
        :return: bottom-left (bl) and top-right(tr) corners
        """
        bl, tr = self.corner1, self.corner2
        # if c1 is on the left of c2
        if self.corner1.x() < self.corner2.x():
            # if c1 is below c2
            if self.corner1.y() < self.corner2.y():
                # we are in the case #1
                bl, tr = self.corner1, self.corner2
            # if c1 is above c2
            elif self.corner1.y() > self.corner2.y():
                # we are in the case #4
                bl = Point3(self.corner1.x(), self.corner2.y(), 0)
                tr = Point3(self.corner2.x(), self.corner1.y(), 0)
        # if c1 is on the right of c2
        elif self.corner1.x() > self.corner2.x():
            # if c1 is below c2
            if self.corner1.y() < self.corner2.y():
                # we are in the case #2
                bl = Point3(self.corner2.x(), self.corner1.y(), 0)
                tr = Point3(self.corner1.x(), self.corner2.y(), 0)
            # if c1 is above c2
            elif self.corner1.y() > self.corner2.y():
                # we are in the case #3
                bl, tr = self.corner2, self.corner1
        return bl, tr

    def select_geometries(self, geoms):
        """
        given a set of geoms return the subset of them that falls within the rectangle
        :param geoms: input geoms
        :return: a set of references to the original geoms
        """

        from app.geoms.point import Point3
        from app.geoms.linestring import LineString
        from app.geoms.polygon import Polygon

        selected_geoms = []
        bl, tr = self.get_classical_bbox()

        for g in geoms:
            all_points_to_check = []
            if isinstance(g, Point3):
                all_points_to_check.append(g)
            elif isinstance(g, LineString):
                for p in g.vertices:
                    all_points_to_check.append(p)
            elif isinstance(g, Polygon):
                for p in g.boundary.vertices:
                    all_points_to_check.append(p)
            else:
                continue

            is_inside = True
            for p in all_points_to_check:
                if not (bl.x() < p.x() < tr.x() and bl.y() < p.y() < tr.y()):
                    is_inside = False
                    break

            if is_inside:
                selected_geoms.append(g)

        return selected_geoms
