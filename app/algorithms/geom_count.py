from app.geoms.point import Point3


def geom_count(geoms, canvas=None):
    return len(geoms)


def geom_count_half(geoms, canvas=None):
    return "The half of the number of geometries in the canvas is: " + str(int(len(geoms)/2))


def my_supercool_new_operation(geoms, canvas=None):
    ret_str = ""

    for g in geoms:
        ret_str += "\n" + str(g)

    return ret_str


def points_centroid(geoms, canvas=None):
    """only consider Points in the canvas. Compute and display
    the centroid obtained by the points."""

    centroid_x = 0
    centroid_y = 0
    centroid_z = 0
    points_num = 0

    for g in geoms:
        if isinstance(g, Point3):
            points_num += 1
            centroid_x += g.x()
            centroid_y += g.y()
            centroid_z += g.z()

    centroid_x /= points_num  # equivalent to centroid_x = centroid_x / points_num
    centroid_y /= points_num
    centroid_z /= points_num

    centroid = Point3(centroid_x, centroid_y, centroid_z)

    canvas.add_geometry(centroid)

    return "The centroid is: " + str(centroid)
