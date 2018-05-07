from app.geoms.utils.transformable import *
from PyQt4.QtCore import pyqtSlot


class CameraTarget(Transformable):
    def __init__(self):
        Transformable.__init__(self)

    def apply_transformation(self):
        pass


class Camera(Transformable):
    VIEW_2D = 1
    VIEW_3D = 2

    ZOOM_MULTIPLIER_3D = 1000
    ORBIT_MULTIPLIER = 2

    def __init__(self):

        Transformable.__init__(self)

        # The center of the view field.
        # Initially, will be placed in (0,0,0) by the method self.reset_view()
        self._target = CameraTarget()

        # the up direction
        self.up_vec = QVector3D(0, 1, 0)

        # distance of the near clipping plane to the camera
        self._viewport_near_plane = 0.001
        # distance of the far clipping plane to the camera
        self._viewport_far_plane = 10000.0

        # zoom multiplier
        self.zoom_level = 1

        # the aspect_ratio will be immediately overwritten when the app starts
        # it will be set equal to the aspect ratio of the canvas
        self._viewport_aspect_ratio = 4 / 3

        # indicates the proportion between a pixel (canvas space) and a world space unit (viewport space)
        self._pixels_per_unit = None  # NOTE: this must be recomputed every time we switch view mode

        # the height (in geometric units) of the viewport (i.e., the height of the near_plane)
        # this value, together with the _viewport_aspect_ratio ( which is the same of the canvas) and the zoom_level
        # is enough to compute the coordinates of the orthographic cube
        self._viewport_height = 50  # NOTE: this must be recomputed every time we switch view mode

        self._view_mode = Camera.VIEW_2D
        self.reset_view()

    #

    # ------------------------
    # PROPERTIES (depending on the few attributes of the camera object)
    # ------------------------
    @property
    def viewport_height(self):
        return self._viewport_height * self.zoom_level

    @property
    def viewport_width(self):
        return self._viewport_height * self._viewport_aspect_ratio * self.zoom_level

    @property
    def viewport_size(self):
        return self.viewport_width, self.viewport_height

    @property
    def viewport_left(self):
        return -self.viewport_width / 2

    @property
    def viewport_right(self):
        return self.viewport_width / 2

    @property
    def viewport_bottom(self):
        return -self.viewport_height / 2

    @property
    def viewport_top(self):
        return self.viewport_height / 2

    @property
    def viewport_near(self):
        return self._viewport_near_plane

    @property
    def viewport_far(self):
        return self._viewport_far_plane

    @property
    def viewport_aspect_ratio(self):
        return self._viewport_aspect_ratio

    @property
    def viewport_fovy(self):
        # field-of-view y (fovy) in degrees.
        # It is twice the angle viewport_top_plane-camera-near_plane
        return degrees(self.viewport_fovy_rad)

    @property
    def viewport_fovy_rad(self):
        # field-of-view y in radians.
        # It is twice the angle viewport_top_plane-camera-near_plane
        return atan2(self.viewport_height / 2, self._viewport_near_plane) * 2

    @property
    def view_mode(self):
        return self._view_mode

    @view_mode.setter
    def view_mode(self, value):
        if value in (Camera.VIEW_2D, Camera.VIEW_3D):
            self._view_mode = value

    @property
    def pixels_per_unit(self):
        return self._pixels_per_unit / self.zoom_level

    @property
    def target(self):
        return self._target

    @property
    def target2camera(self):
        return self.position - self.target.position

    @property
    def camera2target(self):
        return self.target.position - self.position

    @property
    def right_vec(self):
        # the right side (as looking at the target)
        return QVector3D.crossProduct(self.up_vec, self.target2camera).normalized()

    #

    # ------------------------
    # VIEW SET AND RESET FUNCTIONS
    # ------------------------

    @pyqtSlot(bool)
    def set_view_2d(self, toggled):
        if toggled and self._view_mode != Camera.VIEW_2D:
            self._view_mode = Camera.VIEW_2D  # set the _view_mode to VIEW_2D
            self.reset_view()  # reset the position of the camera for 2D View

    @pyqtSlot(bool)
    def set_view_3d(self, toggled):
        if toggled and self._view_mode != Camera.VIEW_3D:
            self._view_mode = Camera.VIEW_3D  # set the _view_mode to VIEW_3D
            self.reset_view()  # reset the position of the camera for 3D view

    @pyqtSlot()
    def reset_view(self):
        # print("Camera.reset_view")
        self.set_target(0, 0, 0)  # reset the target
        self.zoom_level = 1  # reset the zoom

        if self._pixels_per_unit:
            # if true, we are switching from 2D to 3D (or 3D to 2D)
            #
            # then, we have to reset certain parameters and recompute others accordingly
            # for the reinitialization we need to know the actual size of the canvas
            canvas_height = self.viewport_height * self._pixels_per_unit
            canvas_width = self.viewport_width * self._pixels_per_unit

            self._pixels_per_unit = None  # reset the pixels per unit measure

            # reset the viewport_height
            if self._view_mode == Camera.VIEW_2D:
                self._viewport_height = 50  # reset the viewport height for 2D view
            else:
                # when in 3D view it is better to set the fovy and compute the other parameters accordingly
                fovy = 60  # we want a field of view of 60 degrees
                # compute the viewport height accordingly
                self._viewport_height = abs(sin(fovy) * self._viewport_near_plane)

            # now recompute the other parameters (this is done by method resize_view)
            self.resize_view(canvas_width, canvas_height)

        if self._view_mode == Camera.VIEW_2D:
            self._reset_position_2d()
        else:
            self._reset_position_3d()

    def _reset_position_2d(self):
        self.set_position(0, 0, 20)  # reset the position of the camera
        self.up_vec = QVector3D(0, 1, 0).normalized()  # reset the up vector (in 2D mode it is fixed towards the y-axis)

    def _reset_position_3d(self):
        # reset the position and the up vector accordingly!!
        self.set_position_spherical(225.0, 45.0, 50.0)  # reset the position of the camera
        self.up_vec = QVector3D(1, 1, 1).normalized()  # reset the up vector according to the position of the camera

    def resize_view(self, canvas_width, canvas_height):
        if not self._pixels_per_unit:
            # this is fixed only once (in this way we do not deform the view, simply expand/shrink
            # the view area as the canvas expands/shrinks)
            self._pixels_per_unit = canvas_height / self._viewport_height
            # print("setting pixels_per_unit = " + str(self._pixels_per_unit))

        self._viewport_aspect_ratio = canvas_width / canvas_height
        self._viewport_height = canvas_height / self._pixels_per_unit

    #

    # ------------------------
    # Controls: pan, rotate, zoom, and radial_move
    # ------------------------

    def pan(self, delta_x, delta_y):
        # TODO: this could be improved a little bit by splitting the horizontal and vertical padding into two functions
        # TODO: pan becomes xy_pan and only moves the scene on the xy plane
        # TODO: a new function z_pan takes care of moving the scene along the z-axis
        # TODO: both functions triggered by mouse move, but with different key modifiers (e.g. ctrl->xy, ctrl+z->z)

        distance_from_target = abs(self.target2camera.length())

        # translationSpeedInUnitsPerRadius = distance_from_target * self.viewport_top / self.viewport_near
        pixels_per_unit = \
            self.pixels_per_unit * self.viewport_near / distance_from_target if self.view_mode == Camera.VIEW_3D \
            else self.pixels_per_unit

        # print("Right_vec =  " + str(self.right_vec) + " Up_vec =  " + str(self.up_vec))
        movement_vector = self.right_vec * (-delta_x / pixels_per_unit) + self.up_vec * (-delta_y / pixels_per_unit)
        assert isinstance(movement_vector, QVector3D)

        self.move(movement_vector.x(), movement_vector.y(), movement_vector.z())
        self.move_target(movement_vector.x(), movement_vector.y(), movement_vector.z())

    def orbit(self, delta_theta=0, delta_phi=0):
        """
        orbit the camera around the target (which is always at the center of the viewport)
        delta_theta expresses the horizontal rotation:
            rotation around a vector located at the target and pointing towards the positive z-axis
        delta_phi expresses the vertical rotation:
            rotation around the a vector parallel to self.right_vec and translated to the target
        :param delta_theta: horizontal rotation angle
        :param delta_phi: vertical rotation angle
        """

        # orbiting is only allowed in 3D-View mode
        if self.view_mode == Camera.VIEW_3D:

            # get the position wrt the target
            pos2target = self.target2camera
            # get the spherical coords
            pos2target_theta, pos2target_phi, pos2target_radius = cartesian2spherical(pos2target.x(),
                                                                                      pos2target.y(),
                                                                                      pos2target.z())
            # give some speed
            delta_theta *= -1 * Camera.ORBIT_MULTIPLIER
            delta_phi *= 1 * Camera.ORBIT_MULTIPLIER

            # HORIZONTAL ROTATION (theta)
            # no limits on horizontal rotation: the camera can turn all around the target
            # rotate the camera horizontally about the target
            pos2target_theta += delta_theta

            # VERTICAL ROTATION (phi)
            pos2target_phi += delta_phi

            # we do not want the camera to rotate above the target we have a limit of
            if pos2target_phi < 20:
                pos2target_phi = 20
            if pos2target_phi > 160:
                pos2target_phi = 160

            # compute the new position wrt to the target
            new_pos2target = QVector3D(*spherical2cartesian(pos2target_theta,
                                                            pos2target_phi,
                                                            pos2target_radius))
            # compute the new absolute position by adding the target position
            new_absolute_pos = new_pos2target + self.target.position
            # set the new (absolute) position
            self.set_position(new_absolute_pos.x(), new_absolute_pos.y(), new_absolute_pos.z())

            # now we need to update the up vector (the right_vec depends on it, so gets updated as well).
            # Since we never allow the camera to float right above the target, this can be done as follows:
            # 1. compute the new right_vec by cross-producing the camera2target_vec and the vector (0, 1, 0)
            # 2. compute the new up_vec by cross-producing the new right_vec and the camera2target_vec
            camera2target_vec = self.camera2target
            camera2target_normalized = camera2target_vec.normalized()
            new_right_vec = QVector3D.crossProduct(camera2target_normalized, QVector3D(0, 0, 1))
            self.up_vec = QVector3D.crossProduct(new_right_vec, camera2target_normalized)

    def zoom(self, zoom_factor):
        """
        (real zoom), only makes sense in 2D:
        chage the zoom_level to reduce/increase orthographic rendering volume accordingly (because the limits of
        the volume depend on the zoom_level).
        :param zoom_factor: the zoom factor by which the size is changed
        """
        # (real) zoom is only permitted in 2D View
        if self.view_mode == Camera.VIEW_2D and \
            1 < self.viewport_width * zoom_factor < 1000 and \
                1 < self.viewport_width * zoom_factor < 1000:
            self.zoom_level *= zoom_factor

    def move_radial(self, delta_radius=0):
        """
        (fake zoom for 3D)
        Move the camera away/towards the _target (negative values move the camera away)
        """

        # print("\n\ncamera.move_radial(delta_radius=" + str(delta_radius) + ")")
        # the radial move is only allowed in 3D-View mode
        if self._view_mode == Camera.VIEW_3D:
            # get the position wrt the target
            pos2target = self.target2camera
            # get the spherical coords
            pos2target_theta, pos2target_phi, pos2target_radius = cartesian2spherical(pos2target.x(),
                                                                                      pos2target.y(),
                                                                                      pos2target.z())
            # give some speed
            delta_radius *= (-1 / self.pixels_per_unit) * Camera.ZOOM_MULTIPLIER_3D * pos2target.length()
            # print("delta_radius = " + str(delta_radius))

            # move the position along the radius by delta_radius (previously multiplied by some speed value)
            pos2target_radius += delta_radius

            # only move the camera if within the given threshold
            if 0.05 < pos2target_radius < self.viewport_far / 2:
                new_pos2target = QVector3D(*spherical2cartesian(pos2target_theta,
                                                                pos2target_phi,
                                                                pos2target_radius))
                # compute the new absolute position by adding the target position
                new_absolute_pos = new_pos2target + self.target.position
                # set the new (absolute) position
                self.set_position(new_absolute_pos.x(), new_absolute_pos.y(), new_absolute_pos.z())

    #

    # ------------------------
    # update and return view and projection matrices
    # ------------------------

    def get_view_matrix(self):
        view_matrix = QMatrix4x4()
        view_matrix.lookAt(self.position, self.target.position, self.up_vec)
        return view_matrix

    def get_projection_matrix(self):

        # reset the projection matrix
        projection_matrix = QMatrix4x4()  # this is a4x4 numpy.matrix

        # orthographic projection
        if self._view_mode == Camera.VIEW_2D:

            # set the projection matrix to the right orthographic projection
            projection_matrix.ortho(self.viewport_left, self.viewport_right,
                                    self.viewport_bottom, self.viewport_top,
                                    self.viewport_near, self.viewport_far)
        # perspective projection
        else:
            #  set the projection matrix to the right perspective projection
            # print("PROJECTION PARAMS:")
            # print("fovy: " + str(self.viewport_fovy) + " aspect ration:" + str(self.viewport_aspect_ratio) +
            #       " near:" + str(self.viewport_near) + " far:" + str(self.viewport_far))
            projection_matrix.perspective(self.viewport_fovy, self.viewport_aspect_ratio,
                                          self.viewport_near, self.viewport_far)

        return projection_matrix

    #

    # ------------------------
    # UTILITIES
    # ------------------------

    def set_target(self, x, y, z):
        """
        set the position of the _target given a vector of cartesian coordinates
        """
        self._target.set_position(x, y, z)

    def move_target(self, delta_x, delta_y, delta_z):
        self.target.move(delta_x, delta_y, delta_z)

    def canvas2world(self, canvas_x, canvas_y):
        """transforms canvas coords onto world coords"""
        if self.view_mode == Camera.VIEW_2D:
            return canvas_x / self.pixels_per_unit - self.viewport_width/2 + self.target.position.x(), \
                   self.viewport_height / 2 - canvas_y / self.pixels_per_unit + self.target.position.y(),\
                   0
        else:
            # so far, the 3D case is not interesting, maybe in the future
            pass

    def apply_transformation(self):
        pass
