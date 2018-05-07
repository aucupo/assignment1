from PyQt4 import QtCore, QtGui, QtOpenGL
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QPoint
from PyQt4.QtCore import pyqtSlot

from OpenGL import GL


from app.config.params import *
from app.geoms.utils.grid import MyGrid
from app.camera import Camera
from app.geoms.geometry import Geometry
from app.geoms.polygon import Polygon
from app.geoms.point import Point3
from app.geoms.line import Line
from app.geoms.linestring import LineString
from app.geoms.utils.box import Box3D
from app.geoms.utils.selectionbox import SelectionBox

# import ctypes  # it seems to be already contained in some other imported file


class Canvas3d(QtOpenGL.QGLWidget):
    MODE_EXPLORE = 0
    MODE_DRAW = 1
    MODE_SELECT = 2
    MODE_ERASE = 3
    MODE_OPERATION = 4

    DRAW_POINTS = 0
    DRAW_SEGMENTS = 1
    DRAW_POLYGONS = 2
    DRAW_POLYLINES = 3

    def __init__(self, parent=None):
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)

        self.shader_program = None  # QtOpenGL.QGLShaderProgram()

        self.camera = Camera()  # initialize a camera object (initially located at the origin and facing (0, 0, -1)

        self.xy_grid = MyGrid()

        self.renderables3d = set()  # this contains all the geometries on canvas

        self.selection_box = None  # this contains at most 1 selection box

        self.last_mouse_position = QPoint(0, 0)  # last position of the mouse in viewport-coordinates

        self.bounding_box = Box3D(the_min=Point3(-20, -20, -20), the_max=Point3(20, 20, 20))
        # the bounding_box of all the geometries in the canvas.
        # BUT is never smaller than the values set here! Because it is used to set the viewport in VIEW_2D mode

        self.mode = Canvas3d.MODE_EXPLORE  # by default in "scene exploration" mode
        self.draw_what = None  # when in MODE_DRAW, this contains an indication of what is being drawn, else None
        self.currently_drawn_geom = None  # this maintains a reference to a geometry being drawn, until the drawing is complete

        self.selected_geoms = set()  # will contain geometries in the canvas selected via the select tool

        self.canvas_cube_proportion = None
        self.setMouseTracking(True)

    @pyqtSlot(bool)
    def set_mode_explore(self, toggled):
        if toggled:
            self.mode = Canvas3d.MODE_EXPLORE

    @pyqtSlot(bool)
    def set_mode_select(self, toggled):
        if toggled:
            self.mode = Canvas3d.MODE_SELECT

    @pyqtSlot(bool)
    def set_mode_erase(self, toggled):
        if toggled:
            self.mode = Canvas3d.MODE_ERASE

    @pyqtSlot(bool)
    def set_mode_operation(self, toggled):
        if toggled:
            self.mode = Canvas3d.MODE_OPERATION

    @pyqtSlot(bool)
    def set_mode_draw_points(self, toggled):
        if toggled:
            # print("MODE: DRAW_POINTS")
            self.mode = Canvas3d.MODE_DRAW
            self.draw_what = Canvas3d.DRAW_POINTS

    @pyqtSlot(bool)
    def set_mode_draw_segments(self, toggled):
        if toggled:
            self.mode = Canvas3d.MODE_DRAW
            self.draw_what = Canvas3d.DRAW_SEGMENTS

    @pyqtSlot(bool)
    def set_mode_draw_polygons(self, toggled):
        if toggled:
            self.mode = Canvas3d.MODE_DRAW
            self.draw_what = Canvas3d.DRAW_POLYGONS

    @pyqtSlot(bool)
    def set_mode_draw_polylines(self, toggled):
        if toggled:
            self.mode = Canvas3d.MODE_DRAW
            self.draw_what = Canvas3d.DRAW_POLYLINES

    @pyqtSlot(bool)
    def reset_view_2d(self, toggled):
        GL.glDisable(GL.GL_DEPTH_TEST)  # disables the depth test (used to display only "visible" faces)
        GL.glDisable(GL.GL_CULL_FACE)  # disables culling (improves performance as only "visible" faces are processed)

        self.xy_grid.hide()  # hide the grid
        self.camera.set_view_2d(toggled)  # reset the position of the camera for 2D View
        self.setMouseTracking(True)

        self.updateGL()  # update the rendered scene

    @pyqtSlot(bool)
    def reset_view_3d(self, toggled):
        GL.glEnable(GL.GL_DEPTH_TEST)  # enables the depth test (used to display only "visible" faces)
        GL.glEnable(GL.GL_CULL_FACE)  # enables culling (improves performance as only "visible" faces are processed)

        self.drawingEventEnd()  # if we were drawing something end the drawing

        self.xy_grid.show()  # un-hide the grid
        self.camera.set_view_3d(toggled)  # reset the position of the camera for 3D view
        self.window().update_status_bar("3D VIEW")
        self.setMouseTracking(False)
        self.updateGL()  # update the rendered scene


    @pyqtSlot()
    def reset_view(self):
        self.camera.reset_view()  # reset the view
        self.updateGL()  # update the rendered scene

    def mousePressEvent(self, event):
        # when we press a mouse button on the canvas the canvas get the keyboard focus
        self.setFocus()

        # if in drawing mode
        if self.mode == Canvas3d.MODE_DRAW:
            # drawing events are only accepted in 2D View
            if self.camera.view_mode == Camera.VIEW_2D:
                self.drawingEventAddVertex(event=event)

        # if we are in "selection" or "erase" mode
        elif self.mode == Canvas3d.MODE_SELECT or self.mode == Canvas3d.MODE_ERASE:
            # selection events are only accepted in 2D View
            if self.camera.view_mode == Camera.VIEW_2D:
                event_x, event_y, z = self.camera.canvas2world(event.x(), event.y())

                self.selection_box = SelectionBox(Point3(event_x, event_y, 0))

        # update the rendered scene
        self.updateGL()

        self.last_mouse_position = event.pos()
        event.accept()

    def mouseReleaseEvent(self, event):
        # if in drawing mode
        if self.mode == Canvas3d.MODE_DRAW:
            # drawing events are only accepted in 2D View
            if self.camera.view_mode == Camera.VIEW_2D:
                self.drawingEventConfirmLastVertex(event=event)

        # if we are in "selection" mode
        elif self.mode == Canvas3d.MODE_SELECT:
            # selection events are only accepted in 2D View
            if self.camera.view_mode == Camera.VIEW_2D:
                # select geometries inside the box before deleting it
                self.selected_geoms = self.selection_box.select_geometries(self.renderables3d)

                self.window().console_add_line("\nSELECTED SHAPES")
                # self.parent.parent.console_add_line("\nSELECTED SHAPES")
                for g in self.selected_geoms:
                    self.window().console_add_line(str(g))

                self.selection_box = None

        # if we are in "erase" mode
        elif self.mode == Canvas3d.MODE_ERASE:
            # erase events are only accepted in 2D View
            if self.camera.view_mode == Camera.VIEW_2D:
                # select geometries inside the box before deleting it
                selected_geoms = self.selection_box.select_geometries(self.renderables3d)

                for g in selected_geoms:
                    self.remove_geometry(g)

                self.selection_box = None

        # update the rendered scene
        self.updateGL()


        self.last_mouse_position = event.pos()
        event.accept()

    def mouseMoveEvent(self, event):

        if self.camera.view_mode == Camera.VIEW_2D:
            x, y, z = self.camera.canvas2world(event.x(), event.y())
            self.window().update_status_bar("(x, y): ({:.3f}, {:.3f})".format(x, y))

        # if moving while pressing the left button
        if event.buttons() and event.buttons() == QtCore.Qt.LeftButton:
            # if in draw mode: continue drawing
            if self.mode == Canvas3d.MODE_DRAW:
                self.drawingEventMoveLastVertex(event)

            # if we are in "selection" or "erase" mode
            elif self.mode == Canvas3d.MODE_SELECT or self.mode == Canvas3d.MODE_ERASE:
                # selection events are only accepted in 2D View
                if self.camera.view_mode == Camera.VIEW_2D:
                    event_x, event_y, z = self.camera.canvas2world(event.x(),
                                                                   event.y())
                    x, y, z = self.camera.canvas2world(self.last_mouse_position.x(),
                                                       self.last_mouse_position.y())
                    delta_x, delta_y = event_x - x, event_y - y
                    self.selection_box.move_corner2(Point3(delta_x, delta_y, 0))


            # if in exploration mode
            elif self.mode == Canvas3d.MODE_EXPLORE:
                # if no button is held down: pan
                if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.NoModifier:
                    self.panEvent(event)

                # if in 3D View
                if self.camera.view_mode == Camera.VIEW_3D:
                    # if the ctrl (cmd on mac) button is held down: rotate
                    if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
                        self.rotateEvent(event)

        # update the rendered scene
        self.updateGL()

        self.last_mouse_position = event.pos()
        event.accept()

    def keyPressEvent(self, event):
        # if in drawing mode
        if self.mode == Canvas3d.MODE_DRAW:
            # if the escape key is pressed: cancel the current drawing
            if event.key() == QtCore.Qt.Key_Escape:
                # print("pressed Esc")
                self.drawingEventCancel()
            # if either enter or return key is pressed: end the current drawing
            elif event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                # print("pressed Enter")
                self.drawingEventEnd()
            elif event.key() == QtCore.Qt.Key_Backspace:
                self.drawingEventRemoveLastVertex()

        # update the rendered scene
        self.updateGL()

    def wheelEvent(self, event):
        # if scrolling vertically
        if event.orientation() == QtCore.Qt.Vertical:
            # if in exploration mode: zoom
            if self.mode == Canvas3d.MODE_EXPLORE:
                self.zoomEvent(event)

        # update the rendered scene
        self.updateGL()

        event.accept()

    def rotateEvent(self, event):
        delta_x = event.x() - self.last_mouse_position.x()
        # delta_y is computed the opposite way, because the canvas origin is at the up-left corner
        # with positive y-axis point downwards
        delta_y = self.last_mouse_position.y() - event.y()

        # ORBIT (i.e., rotate) the camera around the camera._target
        self.camera.orbit(delta_x, delta_y)

    def panEvent(self, event):
        delta_x = event.x() - self.last_mouse_position.x()
        # delta_y is computed the opposite way, because the canvas origin is at the up-left corner
        # with positive y-axis point downwards
        delta_y = self.last_mouse_position.y() - event.y()

        # PAN the scene by altering camera._target
        self.camera.pan(delta_x, delta_y)

    def zoomEvent(self, event):
        delta = event.delta()
        # if in 3D View mode, the zoom is obtained by changing the distance of the camera from the target
        if self.camera.view_mode == Camera.VIEW_3D:
            # MOVE the camera wrt its _target (change the distance to _target)
            self.camera.move_radial(delta)

        # else, the zoom is obtained by changing the size of the viewed area
        else:
            # ZOOM
            if delta < 0:
                self.camera.zoom(1.05)
            elif delta > 0:
                self.camera.zoom(0.95)

            x, y, z = self.camera.canvas2world(event.x(), event.y())
            self.window().update_status_bar("(x, y): ({:.3f}, {:.3f})".format(x, y))

    def drawingEventAddVertex(self, event):
        """if no geometry is being drawn, create one.
        add a vertex to the drawn geometry"""

        # only if in draw mode
        if self.mode == Canvas3d.MODE_DRAW:
            x, y, z = self.camera.canvas2world(event.x(), event.y())
            new_point = Point3(x, y, z)
            if self.draw_what == Canvas3d.DRAW_POINTS:
                self.currently_drawn_geom = new_point
            elif self.draw_what == Canvas3d.DRAW_SEGMENTS:
                if self.currently_drawn_geom is None:
                    self.currently_drawn_geom = Line()
                self.currently_drawn_geom.add_vertex(new_point)
            elif self.draw_what == Canvas3d.DRAW_POLYGONS:
                if self.currently_drawn_geom is None:
                    self.currently_drawn_geom = Polygon()
                self.currently_drawn_geom.add_vertex(new_point)
            elif self.draw_what == Canvas3d.DRAW_POLYLINES:
                if self.currently_drawn_geom is None:
                    self.currently_drawn_geom = LineString()
                self.currently_drawn_geom.add_vertex(new_point)

            if isinstance(self.currently_drawn_geom, Geometry):
                self.add_geometry(self.currently_drawn_geom)

    def drawingEventRemoveLastVertex(self):
        """if possible, remove the last vertex from the drawn geometry (depends on the type of geometry)"""

        # only if in draw mode
        if self.mode == Canvas3d.MODE_DRAW:
            # if a geom is being drawn
            if self.currently_drawn_geom is not None:
                # if the geometry has at least one vertex
                if len(self.currently_drawn_geom) > 0:
                    self.currently_drawn_geom.remove_vertex()

                # if the current geom has no vertices, cancel it
                if len(self.currently_drawn_geom) == 0:
                    self.drawingEventCancel()


    def drawingEventMoveLastVertex(self, event):
        """move the last drawn vertex of the currently drawn geometry"""

        # only if in draw mode
        if self.mode == Canvas3d.MODE_DRAW:
            if self.currently_drawn_geom is not None:
                x, y, z = self.camera.canvas2world(event.x(), event.y())
                if self.draw_what == Canvas3d.DRAW_POINTS:
                    self.currently_drawn_geom.set_coords(x, y, z)
                elif self.draw_what in (Canvas3d.DRAW_SEGMENTS, Canvas3d.DRAW_POLYGONS, Canvas3d.DRAW_POLYLINES):
                    self.currently_drawn_geom.update_vertex(Point3(x, y, z))

    def drawingEventConfirmLastVertex(self, event):
        """this functions does nothing,
        unless the drawn geometry can have at most a fixed number of vertices,
        in which case, end the drawing"""

        # only if in draw mode
        if self.mode == Canvas3d.MODE_DRAW:
            if self.currently_drawn_geom is not None:
                # points and segments have a limited number of vertices. When we reach this amount we end the drawing
                if isinstance(self.currently_drawn_geom, Point3) \
                   or (isinstance(self.currently_drawn_geom, Line) and len(self.currently_drawn_geom) == 2):
                    self.drawingEventEnd()

    def drawingEventCancel(self):
        """cancel the drawing event (including the removal of the geometry drawn so far from the canvas)"""

        # only if in draw mode and there is a geometry being drawn
        if self.mode == Canvas3d.MODE_DRAW and self.currently_drawn_geom is not None:
            self.remove_geometry(self.currently_drawn_geom)
            self.currently_drawn_geom = None

    def drawingEventEnd(self):
        """ends the drawing of the geometry and prepares the canvas for a new drawing"""

        # only if in draw mode and there is a geometry being drawn
        if self.mode == Canvas3d.MODE_DRAW and self.currently_drawn_geom is not None:
                # if the drawn geometry is valid
                if not self.currently_drawn_geom.is_valid():
                    self.remove_geometry(self.currently_drawn_geom)
                self.currently_drawn_geom = None

    def prepare_shader_program(self, v_shader_path="", f_shader_path=""):

        v_shader_file = open(v_shader_path, 'r')
        vertex_shader_code = v_shader_file.read()
        v_shader_file.close()

        f_shader_file = open(f_shader_path, 'r')
        fragment_shader_code = f_shader_file.read()
        f_shader_file.close()

        if not self.shader_program:
            # print("The shader is None, initialize it.")
            self.shader_program = GL.glCreateProgram()
            if not self.shader_program:
                print("ERROR in shader PROGRAM creation")
                return

        # VERTEX SHADER
        # create a vertex shader
        vertex_shader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
        # set shader source_vertex
        GL.glShaderSource(vertex_shader, vertex_shader_code)
        # compile shader
        GL.glCompileShader(vertex_shader)

        # FRAGMENT SHADER
        # create a fragment shader
        fragment_shader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
        # set shader source_vertex
        GL.glShaderSource(fragment_shader, fragment_shader_code)
        # compile shader
        GL.glCompileShader(fragment_shader)

        # build and link the shader program given the vertex and the fragment shader
        GL.glAttachShader(self.shader_program, vertex_shader)
        GL.glAttachShader(self.shader_program, fragment_shader)
        GL.glLinkProgram(self.shader_program)

        # get rid of the shaders as 1. they have been compiled in the program, 2. we do not need them any longer
        GL.glDetachShader(self.shader_program, vertex_shader)
        GL.glDetachShader(self.shader_program, fragment_shader)

        # make the shader program we just compiled the default program to be run
        GL.glUseProgram(self.shader_program)

    def initializeGL(self):
        # set the background color (to white)
        self.qglClearColor(QtGui.QColor(255, 255, 255))

        GL.glDepthMask(GL.GL_TRUE)

        GL.glEnable(GL.GL_POINT_SMOOTH)  # makes point smooth (looks approx like a sphere)
        GL.glPointSize(config_rendering_point_size)  # size of points

        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glLineWidth(config_rendering_line_width)

        GL.glFrontFace(GL.GL_CCW)  # the "front" of a face is those for which vertices are seen in CCW order

        # FOR TRANSPARENCY?
        # GL.glAlphaFunc(GL.GL_GREATER, 0.1)
        # GL.glEnable(GL.GL_ALPHA_TEST)
        # FOR TRANSPARENCY?
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        # load and link the shader program
        self.prepare_shader_program('shaders/vertex_shader.glsl', 'shaders/fragment_shader.glsl')

    def resizeGL(self, width, height):
        """This function is called automatically by QT when a resize event occurs.
        We need to resize the viewport accordingly"""
        # print("resizeGL")

        # resize the viewport
        GL.glViewport(0, 0, width, height)

        # adjust the view accordingly with the new size of the canvas
        self.camera.resize_view(width, height)

    def paintGL(self):
        # print("paintGL")
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # bind (i.e., pass) the up-to-date view matrix to the vertex shader
        loc = GL.glGetUniformLocation(self.shader_program, "u_view")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, self.camera.get_view_matrix().data())

        # bind (i.e., pass) the up-to-date projection matrix to the vertex shader
        loc = GL.glGetUniformLocation(self.shader_program, "u_projection")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, self.camera.get_projection_matrix().data())

        # if visible not hidden, render the xy grid (only visible in 3D mode)
        self.xy_grid.render(self.shader_program)

        # render all the geometries in the canvas
        for renderable in self.renderables3d:
            # print("Going to paint the renderable: " + str(cube.renderable_vertex_array['position']))
            renderable.render(self.shader_program)

        if self.selection_box is not None:
            self.selection_box.render(self.shader_program)

    def add_geometry(self, *geoms):
        """
        add a geometry to the canvas (namely to the list renderables)
        :param geom: the geometry to add
        :return: None
        """
        for geom in geoms:
            self.renderables3d.add(geom)
        self.updateGL()

    def remove_geometry(self, geom):
        """
        removes the given geometry from the canvas
        :param geom: the geometry to be removed
        :return: None
        """
        self.renderables3d.remove(geom)
        self.updateGL()