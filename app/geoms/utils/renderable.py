"""
this class provides all the necessary logic to render geometries with opengl.
NOTE: this class derives from Movable, which equip the class with a model matrix and all necessary functions
for translation, rotation and scaling.
"""

import ctypes
from abc import (
    ABCMeta,
    abstractmethod
)

from OpenGL import GL

from app.geoms.utils.transformable import Transformable
from app.config.params import *

from PyQt4.QtGui import QVector3D


# Python 2 syntax for abstract class
# class Renderable3d:
#     __metaclass__ = ABCMeta

# Python 3 syntax for abstract class (if using python 2 replace the line below with the two above)
class Renderable3d(Transformable, metaclass=ABCMeta):

    def __init__(self, *args, **kwargs):
        """
        initialize a Renderable3d
        :param elements_type: the GL-type of elements (meshes) that will be rendered for this shape
        :param color: the color of this renderable (must be a Color Object)
        """

        # print("Renderable3d.__init__")

        self.elements_type = kwargs.pop('elements_type', GL.GL_POINTS)
        self.color = kwargs.pop('color', Color())
        if not self.color:
            self.color = Color()

        Transformable.__init__(self, *args, **kwargs)

        self.renderable_vertex_array = None
        # renderable_vertex_array MUST be filled using the method update_renderable_arrays.
        # it will contain a numpy array of the form:
        #     np.zeros(vertex_num,
        #         [
        #              ('coords', [
        #                  ('x', np.float32),
        #                  ('y', np.float32),
        #                  ('z', np.float32)
        #              ]),
        #              ('color', [
        #                  ('r', np.float32),
        #                  ('g', np.float32),
        #                  ('b', np.float32),
        #                  ('a', np.float32)
        #              ])
        #              # if needed, normals can be added here
        #         ]
        #     )

        self.renderable_element_array = None
        # renderable_vertex_array MUST be filled using the method update_renderable_arrays.
        # it will contain a numpy array of uints

        self.renderable_outline_element_array = None

        self.VBO_id = None  # the Vertex Buffer Object (VBO) in the GPU for this object
        self.IBO_id = None  # the Index Buffer Object (IBO) in the GPU for this object (it instructs the GPU on
        # how to make faces from the VBO)
        self.OBO_id = None  # the Outline Index Buffer: contains pairs of indices denoting the lines forming
        # the edges of the renderable. NOTE that this is different than the edges of the elements (because we
        # always split a face into triangles, but the outline must only contain "proper" edges)

        # when there is a change in the renderable (e.g., a vertex is added) this variable is set to True, which means
        # that the GPU buffers are out-of-date and have to be updated before the next rendering of the object
        # this variable is set to
        #   - True when the renderables arrays are updated
        #   - False when the GPU buffers are updated
        self.update_GPU_buffers = True

        self.show_outline = True
        self.visible = True

        from app.geoms.dcel.dcel import DCEL
        self.dcel = DCEL()  # the DCEL is used as a middleware between the geometries and the renderables:
        # every geometric object will be represented with a dcel. The DCEL can be traversed to construct
        # renderable_vertex_array and renderable_element_array of the renderable

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    @abstractmethod
    def update_dcel(self):
        """this method must be reimplemented in derived classes"""
        pass

    def update_renderable_arrays(self):
        """
        update the renderable_vertex_array
        parse self.dcel to generate from it renderable_vertex_array and renderable_element_array arrays
        :return:
        """
        # print("Updating renderable arrays")
        self.update_dcel()

        vertices, elements, outline_elements = self.dcel.get_renderable_arrays()

        vertex_num = len(vertices)
        self.renderable_vertex_array = \
            np.zeros(vertex_num,
                     [
                         ('coords', [
                             ('x', np.float32),
                             ('y', np.float32),
                             ('z', np.float32)
                         ]),
                         ('color', [
                             ('r', np.float32),
                             ('g', np.float32),
                             ('b', np.float32),
                             ('a', np.float32)
                         ])
                         # if needed, normals can be added here
                     ]
                     )

        for i, v in enumerate(vertices):
            self.renderable_vertex_array["coords"][i] = (v.point.x(), v.point.y(), v.point.z())
            self.renderable_vertex_array["color"][i] = tuple(self.color.get_rgba())

        self.renderable_element_array = np.array(elements, dtype=np.uint32)
        self.renderable_outline_element_array = np.array(outline_elements, dtype=np.uint32)

        # print("set update_buffers = True")
        self.update_GPU_buffers = True

    def update_vbo(self, usage=GL.GL_STATIC_DRAW):

        # if there is an old vbo (that must be updated) delete it
        if self.VBO_id is not None:
            GL.glDeleteBuffers(1, [self.VBO_id])

        # create a new vbo and save its id
        self.VBO_id = GL.glGenBuffers(1)  # create an empty VBO on GPU side and returns a reference to it (say, its id)
        # GL.glGenBuffers(number_of_buffers_to_generate)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBO_id)  # bind the just-created buffer on GPU to the VBO_id
        # GL.glBindBuffer(buffer_type, buffer_id)

        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.renderable_vertex_array.nbytes, self.renderable_vertex_array, usage)
        # GL.glBufferData(buffer_type, buffer_size, buffer_data, buffer_usage)

        # the buffer has been updated
        self.update_GPU_buffers = False

    def update_ibo(self, usage=GL.GL_STATIC_DRAW):
        if self.renderable_element_array is not None:
            # for comments see update_vbo (it performs the same steps)
            if self.IBO_id is not None:
                GL.glDeleteBuffers(1, [self.IBO_id])

            self.IBO_id = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.IBO_id)
            GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.renderable_element_array.nbytes,
                            self.renderable_element_array, usage)

            self.update_GPU_buffers = False

    def update_obo(self, usage=GL.GL_STATIC_DRAW):
        if self.renderable_outline_element_array is not None:
            # for comments see update_vbo (it performs the same steps)
            if self.OBO_id is not None:
                GL.glDeleteBuffers(1, [self.OBO_id])

            self.OBO_id = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.OBO_id)
            GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.renderable_outline_element_array.nbytes,
                            self.renderable_outline_element_array, usage)

            self.update_GPU_buffers = False

    def render(self, shader_program):
        """
        asks the GPU to draw the figure, which must be already loaded in a VBO and IBO
        Returns
        -------

        """
        if self.visible:
            # print("Rendering: "+str(self))
            # print(str(self.dcel))

            if self.update_GPU_buffers:
                # print("Updating GPU buffers")
                self.update_vbo()
                self.update_ibo()
                self.update_obo()

            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBO_id)  # GPU: consider this vertex buffer object

            stride = self.renderable_vertex_array.strides[0]

            offset = ctypes.c_void_p(0)
            loc = GL.glGetAttribLocation(shader_program, "a_coords")  # the name of the attribute variable in the shader
            GL.glEnableVertexAttribArray(loc)
            GL.glVertexAttribPointer(loc, 3, GL.GL_FLOAT, False, stride, offset)

            offset = ctypes.c_void_p(self.renderable_vertex_array.dtype["coords"].itemsize)
            loc = GL.glGetAttribLocation(shader_program, "a_color")
            GL.glEnableVertexAttribArray(loc)
            GL.glVertexAttribPointer(loc, 4, GL.GL_FLOAT, False, stride, offset)

            loc = GL.glGetUniformLocation(shader_program, "u_color")
            GL.glUniform4f(loc, 1, 1, 1, 1)

            loc = GL.glGetUniformLocation(shader_program, "u_model")
            GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, self._model2world_matrix.data())

            if self.renderable_element_array is not None:
                GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.IBO_id)  # GPU: consider this index buffer object

                GL.glDisable(GL.GL_BLEND)
                GL.glEnable(GL.GL_DEPTH_TEST)
                GL.glEnable(GL.GL_POLYGON_OFFSET_FILL)

                GL.glDrawElements(
                    self.elements_type,  # the type of meshes being drawn (GL_POINTS, GL_LINES, GL_TRIANGLES,...)
                    len(self.renderable_element_array),  # count
                    GL.GL_UNSIGNED_INT,  # type
                    ctypes.c_void_p(0)  # element array buffer offset
                )

                # GL.glEnable(GL.GL_BLEND)

            if self.show_outline and self.renderable_outline_element_array is not None:
                GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.OBO_id)  # GPU: consider this index buffer object

                loc = GL.glGetUniformLocation(shader_program, "u_color")
                GL.glUniform4f(loc, 0, 0, 0, 1)

                GL.glDisable(GL.GL_POLYGON_OFFSET_FILL)
                GL.glEnable(GL.GL_BLEND)
                GL.glDepthMask(GL.GL_FALSE)

                GL.glDrawElements(
                    GL.GL_LINES,  # the type of meshes being drawn (GL_POINTS, GL_LINES, GL_TRIANGLES,...)
                    len(self.renderable_outline_element_array),  # count
                    GL.GL_UNSIGNED_INT,  # type
                    ctypes.c_void_p(0)  # element array buffer offset
                )

                GL.glDepthMask(GL.GL_TRUE)

    def apply_transformation(self):
        for vertex in self.renderable_vertex_array["coords"]:
            vec = QVector3D(vertex[0], vertex[1], vertex[2])
            vec = self._model2world_matrix * vec
            vertex[0], vertex[1], vertex[2] = vec.x(), vec.y(), vec.z()

    def set_color(self, color=None):
        if color is not None and isinstance(color, Color):
            self.color = color
        else:
            self.color = Color()
