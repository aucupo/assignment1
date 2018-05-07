import numpy as np


class Vector(np.ndarray):

    def __new__(cls, *args, **kwargs):
        # print("Vector.__new__")
        if isinstance(args[0], Vector):
            # copy-constructor
            obj = np.array(args[0].tolist(), dtype=np.float32, copy=True, subok=True)
        elif isinstance(args, (list, tuple, np.ndarray, Vector)) \
                and all(isinstance(i, (int, float,
                                       np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64,
                                       np.uint8, np.uint16, np.uint32, np.uint64,
                                       np.float_, np.float16, np.float32, np.float64)) for i in args):
            obj = np.array(args, dtype=np.float32, copy=True, subok=True)
        else:
            raise TypeError(str(cls) +
                            ".__new__ accepts only array-like parameters of numeric type")

        return obj.view(cls)

    def __str__(self):
        return self.__class__.__name__ + repr(self)

    def __repr__(self):
        return "(" + ", ".join([str(x) for x in self]) + ")"

    def __eq__(self, other):
        return np.array_equal(self, other)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        coords_concatenation = ""
        for elem in self:
            coords_concatenation += str(elem)
        return hash(coords_concatenation)

    def __add__(self, other):
        return self.__class__(np.ndarray.__add__(self, other))

    def __sub__(self, other):
        return self.__class__(np.ndarray.__sub__(self, other))

    def magnitude(self):
        sum_of_squares = 0
        for x in self:
            sum_of_squares += x ** 2

        return sum_of_squares ** (1 / 2)

    def norm(self):
        n = len(self)
        nth_sum = 0
        for x in self:
            nth_sum += x ** n

        return nth_sum ** (1 / n)

    def normalize(self):
        """returns a normalized copy (a versor) of self"""
        magnitude = self.magnitude()

        # normalize the copy by dividing each coordinates by the magnitude
        copy = self / magnitude

        return copy.view(self.__class__)  # needed for returning the appropriate (sub)-class


class Vector2(Vector):

    def __new__(cls, *args, **kwargs):
        # print("Vector2.__new__")

        # first, create a Vector obj
        obj = Vector.__new__(cls, *args, **kwargs)

        # 2d vectors must have exactly 2 elements
        if len(obj) > 2:
            obj = obj[:2]
        else:
            # if it has less then two elements append enough zeros to get a 2d vector
            while len(obj) < 2:
                obj = np.append(obj, [0.0])

        return obj.view(cls)

    def x(self):
        """Property x is first element of vector."""
        return self[0]

    def set_x(self, value):
        self[0] = value

    def y(self):
        """Property y is second element of vector."""
        return self[1]

    def set_y(self, value):
        self[1] = value


class Vector3(Vector):

    def __new__(cls, *args, **kwargs):
        # print("Vector3.__new__")

        # first, create a Vector obj
        obj = Vector.__new__(cls, *args, **kwargs)

        # 3d vectors must have exactly 3 elements
        if len(obj) > 3:
            obj = obj[:3]
        else:
            # if it has less then three elements append enough zeros to get a 3d vector
            while len(obj) < 3:
                obj = np.append(obj, [0.0])

        return obj.view(cls)

    def x(self):
        """Property x is first element of vector."""
        return self[0]

    def set_x(self, value):
        self[0] = value

    def y(self):
        """Property y is second element of vector."""
        return self[1]

    def set_y(self, value):
        self[1] = value

    def z(self):
        """Property 2 is third element of vector."""
        return self[2]

    def set_z(self, value):
        self[2] = value

    def theta(self):
        """when the vector is used for spherical coordinates"""
        return self[0]

    def set_theta(self, value):
        self[0] = value

    def phi(self):
        """when the vector is used for spherical coordinates"""
        return self[1]

    def set_phi(self, value):
        self[1] = value

    def radius(self):
        """when the vector is used for spherical coordinates"""
        return self[2]

    def set_radius(self, value):
        self[2] = value

    def cross(self, other):
            return Vector3(self.y()*other.z() - self.z()*other.y(),
                           self.z()*other.x() - self.x()*other.z(),
                           self.x()*other.y() - self.y()*other.x())

    def __mul__(self, other):
        """NOTE!!! this implementation only considers the multiplication by a 4x4 transformation matrix"""
        if isinstance(other, np.ndarray):
            other = np.matrix(other)
        if isinstance(other, np.matrix):
            if other.shape == (4, 4):
                self_list = self.tolist()
                self_list.append(1)
                vec4 = np.array(self_list, dtype=np.float32)
                res_list = other.dot(vec4).tolist()[0]
                return Vector3(*res_list)
