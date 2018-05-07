from app.geoms.utils.renderable import Renderable3d
from app.geoms.geometry import Geometry
from app.geoms.utils.box import Box3D

from app.geoms.utils.constants import *

from app.utils.vector import Vector, Vector3


class Point(Vector):
    def __new__(cls, *args, **kwargs):
        # print("Point.__new__")
        return Vector.__new__(cls, *args, **kwargs)


class Point3(Point, Vector3, Geometry, Renderable3d):
    def __new__(cls, *args, **kwargs):
        # print("Point3.__new__")
        return Vector3.__new__(cls, *args, **kwargs)  # No need to call Point constructor as it would not
        # add anything. YET, it important to inherit from BasePoint so we can more easily check that something
        # is a point

    def __init__(self, *args, **kwargs):
        # print("Point3.__init__")

        Geometry.__init__(self, *args, **kwargs)
        Renderable3d.__init__(self, *args, **kwargs)

        self.update_substructures()


    def update_substructures(self):
        self.update_bounding_box()
        self.update_renderable_arrays()


    def update_dcel(self):
        # print("Point3.update_dcel")
        self.dcel.make_from_points(self)


    def update_bounding_box(self):
        self.bounding_box.set_min(self)
        self.bounding_box.set_max(self)


    def set_coords(self, x=None, y=None, z=None):
        if x is not None:
            Vector3.set_x(self, x)

        if y is not None:
            Vector3.set_y(self, y)

        if z is not None:
            Vector3.set_z(self, z)

        self.update_substructures()


    def set_x(self, value):
        Vector3.set_x(self, value)
        self.update_substructures()


    # test comment for git integration
    # yet another test comment for git integration

    def set_y(self, value):
        Vector3.set_y(self, value)
        self.update_substructures()


    def set_z(self, value):
        Vector3.set_z(self, value)
        self.update_substructures()


    def is_valid(self):
        return self.x() is not None and self.y() is not None and self.z() is not None


    def __hash__(self):
        """Allows for using a Geometry as a key of a set or a dictionary."""
        return hash(id(self))


    @staticmethod
    def random(bbox, points_num=1):
        assert (isinstance(bbox, Box3D))

        bbox_min, bbox_max = bbox.min(), bbox.max()
        from random import uniform
        random_points = list()
        for i in range(points_num):
            random_x = uniform(bbox_min.x(), bbox_max.x())
            random_y = uniform(bbox_min.y(), bbox_max.y())
            random_z = uniform(bbox_min.z(), bbox_max.z())
            random_points.append(Point3(random_x, random_y, random_z))

        return random_points


    @staticmethod
    def raw_orientation(a, b, c, d):
        """
        compute the orientation of three points (a, b, c) as seen from a fourth point (d)
        in other words, checks the direction of the turn as moving from a to b to c CCW=LEFT, CW=RIGHT,
        COLLINEAR=STRAIGHT
        :return: CCW, CW, Collinear if the points are not coplanar, False otherwise
        """

        from app.geoms.tetrahedron import Tetrahedron
        # compute the volume of the tetrahedron formed by the points
        signed_vol = Tetrahedron.signed_volume(a, b, c, d)

        if signed_vol < -EPSILON:
            return CCW
        elif signed_vol > EPSILON:
            return CW
        else:
            # the four points are coplanar, so we have to use a different approach to determine the orientation
            # we must use the cross-product rule with the first 3 points
            ab = b - a  # vector ab
            ac = c - a  # vector ac

            cross_magnitude = ab.cross(ac).magnitude()

            if cross_magnitude > EPSILON:
                return CCW
            elif cross_magnitude < -EPSILON:
                return CW
            else:
                return COLLINEAR


    @staticmethod
    def collinear_position(a, b, c):
        """
        this function must be called only when it is known that the three input points are COLLINEAR, otherwise
        produces meaningless results
        :param a: Point
        :param b: Point
        :param c: Point
        :return: BEFORE, BETWEEN, or AFTER (the position of c wrt a->b)
        """

        # a and b must not coincide, otherwise makes no sense
        if a == b:
            return False

        # to compute the result we can use the distances between the points
        a_b = a.distance(b)
        a_c = a.distance(c)
        b_c = b.distance(c)

        if a_c + b_c > a_b:
            if a_c < b_c:
                return BEFORE
            else:
                return AFTER
        else:
            return BETWEEN


    @staticmethod
    def orientation(a, b, c, d):
        """
        return the position of the point c when going from a to b, as seen from observation point d
        :param a: Point3
        :param b: Point3
        :param c: Point3
        :param d: Point3
        :return: LEFT, RIGHT, BEFORE, BETWEEN, or AFTER
        """

        orientation = Point3.raw_orientation(a, b, c, d)
        if orientation == CCW:
            return LEFT
        elif orientation == CW:
            return RIGHT
        else:  # COLLINEAR
            # if _collinear, we need to determine where exactly (BEFORE, BETWEEN, or AFTER)
            # for this we can use the distances between the points
            return Point3.collinear_position(a, b, c)



    @staticmethod
    def _coplanar(*points):
        """
        :param points: a tuple of Point objects
        :return: True if the points are all coplanar, False otherwise
        """

        from app.geoms.tetrahedron import Tetrahedron
        if not all(isinstance(p, Vector3) for p in points):
            raise TypeError("Point.Coplanar() Arguments must be Vector3 objects")

        unique_points = list(set(points))  # remove "duplicates" (points with same coordinates)

        if len(unique_points) == 0:
            # no points given
            return False

        if len(unique_points) < 4:
            # 1, 2, or 3 points are always _coplanar
            return True

        # normalize the points wrt to the first point in the unique point list
        first_point = Point3(unique_points[0])
        normalized_points = [p - first_point for p in unique_points]

        # all quadruplets p1, p2, p3, p4 must be _coplanar (where p4 is any other point than p1, p2, and p3)
        for p4 in normalized_points[3:]:
            # four points are coplanar if the volume of the tetrahedron they form is 0
            # if tetrahedron_signed_volume(p1, p2, p3, p4) != 0:
            # print(str(tetrahedron_signed_volume(p1, p2, p3, p4)))
            if not (-EPSILON <= Tetrahedron.signed_volume(*normalized_points[0:3], p4) <= EPSILON):
                return False

        return True


    @staticmethod
    def are_coplanar(*points):
        return Point3._coplanar(*points)


    def is_coplanar_with(self, *points):
        return Point3._coplanar(self, *points)


    @staticmethod
    def _collinear(*points):
        """
        take a list of points and determine if they are collinear
        :param points:
        :return: True/False
        """

        if not all(isinstance(p, Vector3) for p in points):
            raise TypeError("Arguments must be 3-vectors")

        unique_points = list(set(points))  # remove "duplicates" (points with same coordinates)

        if len(unique_points) == 0:
            # no points given
            return False

        if len(unique_points) < 3:
            # less 1 or 2 points are always collinear
            return True

        # in order to be collinear the points have to be coplanar
        if not Point3._coplanar(*unique_points):
            return False

        # normalize the points wrt to the first point in the unique point list
        normalized_points_except_first = [p - unique_points[0] for p in unique_points[1:]]
        # all triplets p1, p2, p3 must be _collinear (where p3 is any other point than p1 and p2)
        for next_point in normalized_points_except_first[1:]:
            if not (-EPSILON <= (normalized_points_except_first[0].cross(next_point)).magnitude() <= EPSILON):
                return False

        return True


    @staticmethod
    def are_collinear(*points):
        return Point3._collinear(*points)


    def is_collinear_with(self, *points):
        return Point3._collinear(self, *points)


    def distance(self, other):
        """
        :param other: Point3
        :return: the distance between self and other
        """

        # NOTE: the distance is the magnitude of the vector from self to other
        return Vector3(other - self).magnitude()

    def wkt(self):
        return "POINT({} {} {})".format(self.x(), self.y(), self.z())

    def __str__(self):
        return "{}({} {} {})".format(self.__class__.__name__, self.x(), self.y(), self.z())


