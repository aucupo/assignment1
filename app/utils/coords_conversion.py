from math import *


def spherical2cartesian(theta, phi, radius):
    x = radius * cos(radians(theta)) * sin(radians(phi))
    y = radius * sin(radians(theta)) * sin(radians(phi))
    z = radius * cos(radians(phi))
    return x, y, z


def cartesian2spherical(x, y, z):
    radius = sqrt(x**2 + y**2 + z**2)
    if radius == 0:
        phi, theta = 0, 0
    else:
        phi = degrees(acos(z / radius))
        theta = degrees(atan2(y, x))

    return theta, phi, radius


