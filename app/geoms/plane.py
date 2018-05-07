from app.geoms.point import Point3
from app.utils.vector import Vector3


class Plane(object):
    """
    Plane class: default to xy plane
    """

    def __init__(self, p=Point3(0, 0, 0), p1=None, p2=None, normal=Vector3(0, 0, 1)):
        """
        a plane can be defined either by three non-_collinear points or by a point and a vetor denotin the normal
        to the plane. The normal vector has priority over the points. I.e., if both the normal vector and points 1 and 2
        are given, p1 and p2 are ignored
        :param p: the first point
        :param p1: the second point (mutually exclusive with normal)
        :param p2: the third point (mutually exclusive with normal)
        :param normal: the normal vector (mutually exclusive with point 1 and 2)
        """
        self._position = p

        if normal and isinstance(normal, Vector3):
            self._normal = normal / normal.magnitude()  # normalize the vector (i.e., magnitude = 1)
        elif p1 and isinstance(p1, Point3) and p2 and isinstance(p2, Point3):
            if Point3.are_collinear(p, p1, p2):
                # if the three points are _collinear raise an error
                raise ValueError('To define a plane three non-_collinear points must be given')

            # compute the normal to the triangle p-p1-p2
            cross_prod = (p2-p).cross(p2 - p)
            self._normal = cross_prod / cross_prod.magnitude  # normalize the vector (i.e., magnitude = 1)


    # TODO: return 1 if point is in the half-space pointed by direction, -1 if on the other, 0 if on the plane
    def __point_position(self, a_point):
        pass

class PlaneFactory(object):
    def make_plane_parallel_to_line_and_passing_2_points(self, vec, p1, p2):
        # vec is a vector representing the line that the plane must be parallel to
        vec2 = p1-p2  # the vector going from p1 to p2 is (trivially) parallel to the plane to generate

        normal = vec.cross(vec2)

        if normal.magnitude() == 0:
            # TODO: resolve special cases(see commented lines below)
            raise Exception("Cannot create plane parallel to line and passing for 2 points (TODO)")
            # # this happens when the vec and vec2 are parallel or _collinear
            # if Line(vec).is_collinear_with(vec2):
            #     # if they are _collinear we return a plane parallel to the xy plane
            #     pass
            # else:
            #     return Plane(p=p1, p1= p2, p2=Point3(vec))

        return Plane(p1, normal=normal)