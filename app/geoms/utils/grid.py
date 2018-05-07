from app.geoms.utils.renderable import Renderable3d

from app.config.params import *

from OpenGL import GL

class MyGrid(Renderable3d):
    def __init__(self):

        # get some parameters from config file
        grid_color = config_rendering_grid_color
        row_num = config_rendering_grid_row_num
        col_num = config_rendering_grid_col_num
        cell_size = config_rendering_grid_cell_size

        Renderable3d.__init__(self, elements_type=GL.GL_LINES, color=grid_color)

        self.visible = False  # we start with a 2D view_mode where the grid must be hidden

        # for convenience is better to have always an even number of rows and cols
        if row_num % 2 != 0:
            row_num += 1
        if col_num % 2 != 0:
            col_num += 1

        # a grid with row_num rows and col_num columns
        # that is
        # - row_num+1 x-aligned segments
        # - col_num-1 y-aligned segments
        # each segment is defined by two vertices, so...
        vertex_num = (row_num + 1 + col_num + 1) * 2


        # prepare the elements array
        self.renderable_outline_element_array = np.zeros((row_num+1+col_num+1)*2, dtype=np.uint32)

        self.renderable_vertex_array = np.zeros(vertex_num,
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

        z = 0
        # ADD the vertices defining the rows
        mid_row = row_num/2
        x_left = -col_num/2 * cell_size
        x_right = col_num / 2 * cell_size
        for i in range(row_num+1):
            y = (mid_row - i) * cell_size
            self.renderable_vertex_array["coords"][i*2] = (x_left, y, z)
            self.renderable_vertex_array["color"][i * 2] = tuple(self.color.get_rgba())
            self.renderable_vertex_array["coords"][(i * 2)+1] = (x_right, y, z)
            self.renderable_vertex_array["color"][(i * 2)+1] = tuple(self.color.get_rgba())

            self.renderable_outline_element_array[i * 2] = i * 2
            self.renderable_outline_element_array[(i * 2) + 1] = (i * 2) + 1

        # ADD the vertices defining the columns
        offset = row_num+1
        mid_col = col_num / 2
        y_bottom = -row_num / 2 * cell_size
        y_top = row_num / 2 * cell_size
        for i in range(col_num + 1):
            x = (mid_col - i) * cell_size
            self.renderable_vertex_array["coords"][(offset+i) * 2] = (x, y_bottom, z)
            self.renderable_vertex_array["color"][(offset+i) * 2] = tuple(self.color.get_rgba())
            self.renderable_vertex_array["coords"][((offset+i) * 2) + 1] = (x, y_top, z)
            self.renderable_vertex_array["color"][((offset+i) * 2) + 1] = tuple(self.color.get_rgba())

            self.renderable_outline_element_array[(offset+i) * 2] = (offset+i) * 2
            self.renderable_outline_element_array[((offset+i) * 2) + 1] = ((offset+i) * 2) + 1

        # print(str(self.vertices))
        # print(str(self.renderable_outline_element_array))


    def update_dcel(self):
        pass

    def render(self, shader_program):
        # the width of the lines making the grid is different than that of normal lines
        GL.glLineWidth(config_rendering_grid_line_with)  # set line width for the grid
        Renderable3d.render(self, shader_program=shader_program)
        GL.glLineWidth(config_rendering_line_width)  # set line width for other lines



#g = MyGrid()