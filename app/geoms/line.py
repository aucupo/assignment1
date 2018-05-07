from app.geoms.linestring import LineString
from app.geoms.point import Point3

from app.geoms.utils.constants import *

from app.utils.vector import Vector2, Vector3


class Line(LineString):
    def __init__(self, vertices=None, vector=None, color=None):
        """
        creates a Line. if start and end are not given makes a degenerate segment (a point at the origin).
        if vector is given and is a Vector3 makes a segment going from the origin to the coordinates of the vector
        """

        if vector and isinstance(vector, Vector3):
            vertices = [Point3(0, 0, 0), Point3(vector)]

        if vertices and len(vertices) > 2:
            vertices = vertices[:2]
        LineString.__init__(self, vertices=vertices, color=color)

    @property
    def start(self):
        return self[0]

    @start.setter
    def start(self, val):
        self[0] = val

    @property
    def end(self):
        return self[1]

    @end.setter
    def end(self, val):
        self[1] = val

    @staticmethod
    def _collinear(*segments):
        if not all(isinstance(s, Line) for s in segments):
            raise TypeError("Line._collinear requires all Line objects")

        unique_segments = list(set(segments))

        if len(unique_segments) == 0:
            return False
        elif len(unique_segments) == 1:
            return True
        else:
            points = []
            for s in segments:
                points.append(s.start)
                points.append(s.end)

            return Point3.are_collinear(*points)

    def length(self):
        return (self.end-self.start).magnitude()

    def add_vertex(self, v, i=None):
        """
        adds a vertex to the segment, but only if the current number of vertices is <2
        :param v:
        :param i:
        :return:
        """
        if len(self) < 2:
            return LineString.add_vertex(self, v, i)

    @staticmethod
    def are_collinear(*segments):
        return Line._collinear(*segments)

    def is_collinear_with(self, *segments):
        return Line._collinear(self, *segments)

    @staticmethod
    def _parallel(*segments):
        """
        two segments are parallel if, translating both to the origin we have two COLLINEAR segments
        """
        if not all(isinstance(s, Line) for s in segments):
            raise TypeError("Line._parallel requires all Line objects")

        unique_segments = list(set(segments))

        if len(unique_segments) == 0:
            return False
        elif len(unique_segments) == 1:
            return True
        else:
            # take the first segment and translate it to the origin
            first_translated_seg = Line([Point3(0, 0, 0), (segments[0].end - segments[0].start)])

            # the given segments are parallel if they are all parallel to the first
            for s in segments[1:]:
                translated_seg = Line([Point3(0, 0, 0), (s.end - s.start)])
                if not first_translated_seg.is_collinear_with(translated_seg):
                    return False

            return True

    @staticmethod
    def are_parallel(*segments):
        return Line._parallel(*segments)

    def is_parallel_with(self, *segments):
        return Line._parallel(self, *segments)

    def point_position(self, a_point, perspective_point=Point3(0, 0, 1)):
        """
        Check the position of a_point w.r.t. the segment on the plane formed by the segment and the point,
        as viewed from the perspective_point
        :param a_point: a Point object
        :param perspective_point: observation point (the default value should be used ONLY when working in 2D)
        :return: False, if the perspective point is COPLANAR with self and the a_point;
                 otherwise, either RIGHT (-1), LEFT (1), BEFORE (-2), BETWEEN (0), or AFTER (2)
        """

        if Point3.are_coplanar(self.start, self.end, a_point, perspective_point):
            return False

        return Point3.orientation(self.start, self.end, a_point, perspective_point)

    def intersects(self, other):
        """
        :param other: Line or Vector
        :return: True if the two segments intersect, False otherwise
        """

        if isinstance(other, (Vector2, Vector3)):
            other = Line([Point3(0, 0, 0), Point3(other)])

        if not isinstance(other, Line):
            raise TypeError("Line.intersects requires a Line or a Vector as parameter")

        l1, l2 = self, other  # handy aliases for the segments

        # in order for two segments to intersect they must lie on the same plane
        if not Point3.are_coplanar(l1.start, l1.end, l2.start, l2.end):
            print("Segments are not COPLANAR")
            return False

        # Ok, the segments are COPLANAR!
        # now, we have two cases to be treated separately: (1) the segments are COLLINEAR, (2) or not

        if l1.is_collinear_with(l2):
            # if COLLINEAR we need to check the relative distances between the extremes of the segments

            # We have only three possible cases where the segments intersect:
            # A) l2 is inside l1 (i.e., both l2 extremes are BETWEEN l1 extremes)
            # B) l1 is inside l2
            # C) none of the above, but one extreme of one of the two segments is BETWEEN the extremes of the other

            # compute the positions of the segments' extremes wrt the other segment
            l2_start_position = Point3.collinear_position(l1.start, l1.end, l2.start)
            l2_end_position = Point3.collinear_position(l1.start, l1.end, l2.end)
            l1_start_position = Point3.collinear_position(l2.start, l2.end, l1.start)
            l1_end_position = Point3.collinear_position(l2.start, l2.end, l1.end)

            # case A)
            if l2_start_position == BETWEEN and l2_end_position == BETWEEN:
                return True
            # case B)
            elif l1_start_position == BETWEEN and l1_end_position == BETWEEN:
                return True
            # case C)
            elif any(pos == BETWEEN
                     for pos in [l2_start_position, l2_end_position, l1_start_position, l1_end_position]):
                return True
            else:
                return False

        else:
            # if the two segments are not COLLINEAR, it can still be the case that one of the extremes of
            # one segment is COLLINEAR with the other segment. This case must be treated separately

            # consider l1 as reference segment and check if the extremes of l2 are COLLINEAR with l1
            is_l2_start_collinear = Point3.are_collinear(l1.start, l1.end, l2.start)
            is_l2_end_collinear = Point3.are_collinear(l1.start, l1.end, l2.end)

            # consider l2 as reference segment and check if the extremes of l1 are COLLINEAR with l2
            is_l1_start_collinear = Point3.are_collinear(l2.start, l2.end, l1.start)
            is_l1_end_collinear = Point3.are_collinear(l2.start, l2.end, l1.end)

            if is_l2_start_collinear or is_l2_end_collinear or is_l1_start_collinear or is_l1_end_collinear:
                # NOTE: at most one of the above variables can be True, otherwise it means that the two
                # segments are COLLINEAR and we would have entered the if condition above--l1.is_collinear_with(l2).

                # determine which is the reference segment
                ref_segment = l1 if is_l2_start_collinear or is_l2_end_collinear else l2

                # determine which extreme of the other segment is COLLINEAR with the ref_segment
                # assume it is l2.start
                coll_extreme = l2.start
                if ref_segment is l1:
                    if is_l2_end_collinear:
                        coll_extreme = l2.end
                else:
                    if is_l1_start_collinear:
                        coll_extreme = l1.start
                    else:
                        coll_extreme = l2.end

                # the only case when the two segments intersect is when the coll_extreme is positioned
                # BETWEEN the extremes of the reference segment
                return Point3.collinear_position(ref_segment.start, ref_segment.end, coll_extreme) == BETWEEN

            else:
                # the two segments are in general position. So, to determine if they intersect
                # we need to check the position of the extremes of each segment wrt the other segment.
                # To do this in 3-space we need an observation point that is not on the same plane
                # so, compute an observation point that is not on the same plane

                #  easily, we can take the cross product of the two segments
                v1 = Vector3(l1.end - l1.start)
                v2 = Vector3(l2.end - l2.start)
                v3 = v1.cross(v2)
                observation_point = Point3(v3) + l1.start

                # in order to intersect the extremes of each segment must lie on opposite sides of the other segment
                return \
                    l1.point_position(l2[0], observation_point) * l1.point_position(l2[1], observation_point) < 0 and \
                    l2.point_position(l1[0], observation_point) * l2.point_position(l1[1], observation_point) < 0

    def intersection(self, other):
        # self= [p,p+r]; other=[q,q+other]
        if isinstance(other, Line):  # if other is actually a segment
            if self.intersects(other):  # if the segments intersect
                # print("INTERSECT")
                p = Vector3(self.vertices[0])
                q = Vector3(other.vertices[0])
                r = Vector3(self.vertices[1] - self.vertices[0])
                s = Vector3(other.vertices[1] - other.vertices[0])

                if not self.is_collinear_with(other):  # general case
                    # print("NOT COLLINEAR")

                    t = (q - p).cross(s)[2] / r.cross(s)[2]

                    return Point3(p.x() + t * r.x(), p.y() + t * r.y())

                else:  # special case: collinear segments
                    # print("COLLINEAR")

                    # position of other.vertices[0] wrt self.vertices[0],self.vertices[1]
                    s0_pos = Point3.collinear_position(self.vertices[0], self.vertices[1], other.vertices[0])

                    # position of other.vertices[1] wrt self.vertices[0],self.vertices[1]
                    s1_pos = Point3.collinear_position(self.vertices[0], self.vertices[1], other.vertices[1])

                    start = None
                    end = None

                    # if one vertex of other is before self
                    if s0_pos == BEFORE or s1_pos == BEFORE:
                        # print("ONE VERTEX OF S IS BEFORE")
                        start = self.vertices[0]  # the resulting segment starts at self[0]
                        if s0_pos == BETWEEN:
                            # print("S[0] IS BETWEEN")
                            end = other.vertices[0]
                        elif s1_pos == BETWEEN:
                            # print("S[1] IS BETWEEN")
                            end = other.vertices[1]
                        elif s0_pos == AFTER or s1_pos == AFTER:
                            # print("THE OTHER VERTEX IS AFTER")
                            end = self.vertices[1]

                    # otherwise, at least one vertex of other must lie between self[0] and self[1]
                    # (because we know they intersect and are collinear)
                    else:
                        # print("ONE VERTEX OF S IS BETWEEN")
                        # assume other is completely inside self
                        start = other.vertices[0]  # then the intersection coincides with other
                        end = other.vertices[1]

                        if s0_pos == AFTER:
                            start = self.vertices[1]  # the intersection starts at self[1]
                        elif s1_pos == AFTER:
                            end = self.vertices[1]  # the intersection ends at self[1]

                    # print("start:"+str(start))
                    # print("end:"+str(end))
                    if start != end:

                        return Line(vertices=[Point3(start), Point3(end)])
                    else:
                        return Point3(start)

        return None

    def __hash__(self):
        """Allows for using a Geometry as a key of a set or a dictionary."""
        return hash(id(self))
