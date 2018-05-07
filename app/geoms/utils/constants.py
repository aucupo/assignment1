# NOTE: it is a good idea not to use 0 for constants because 0 evaluates to False while any other number evaluates to
# True. In this way, when calling a function that returns a constant we can easily verify that the function worked
# correctly, while, if there was some strange condition that did not allow to compute the result the function returns
# 0/False

LEFT = CCW = 1  # Counter Clock Wise
RIGHT = CW = -1  # Clock Wise

BETWEEN = COLLINEAR = 10  # one or more geometries lie on the same line; also, Collinear/go-straight/no-turn
BEFORE = -2  # _collinear and before
AFTER = 2  # _collinear and after

COPLANAR = 20  # one or more 3D geometries lie on the same plane

EPSILON = 0.00001




