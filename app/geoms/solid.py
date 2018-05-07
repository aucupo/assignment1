from app.geoms.utils.renderable import Renderable3d

from OpenGL import GL


class Solid(Renderable3d):

    def __init__(self, color=None):
        Renderable3d.__init__(self, elements_type=GL.GL_TRIANGLES, color=color)

    # def update_renderable_arrays(self):
    #     """
    #     solids are built differently than points, lines and polygons.
    #     Namely, the renderable arrays are hardcoded in the init function.
    #     That is, a solid is built from a template. The only exception is the generic Polyhedron
    #     that is built from a set of points (by computing their convex hull)
    #     """

    def update_dcel(self):
        self.dcel.make_from_solid(self)
