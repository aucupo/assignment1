from app.algorithms.print_geoms import *
from app.algorithms.geom_count import *


# a utility class to collect all necessary info about a tool
class Tool(object):
    def __init__(self, *args, **kwargs):
        self.obj_type = kwargs.pop('obj_type', "radio")  # the form-type of the tool (radiobutton, button, combobox,...)
        self.obj_name = kwargs.pop('obj_name', "")  # the name of the object as defined in the QtDesigner
        self.status_text = kwargs.pop('status_text', "")  # the text to be shown in the status bar when tool is selected
        self.info_text = kwargs.pop('info_text', "")  # the text to be shown in the info_box
        self.items = kwargs.pop('items', dict())
        # a dictionary "op_name": Tool object (containing info on the func to be called)
        self.operation_func = kwargs.pop('operation_func', None)  # a reference to the function to be called


#   configuration of tools_2d
tools_2d = dict()  # will contain config info for all 2d tools

tools_2d["tool2d_explore_radio"] = \
    Tool(obj_name="tool2d_explore_radio",
         status_text="Exploring the scene",
         info_text="Pan: hold the mouse left button and move the mouse."
                   "\nZoom: scroll wheel")

tools_2d["tool2d_draw_points_radio"] = \
    Tool(obj_name="tool2d_draw_points_radio",
         status_text="Drawing points",
         info_text="Left-click anywhere on the canvas to set a point. The point is set on button release.")

tools_2d["tool2d_draw_segments_radio"] = \
    Tool(obj_name="tool2d_draw_segments_radio",
         status_text="Drawing segments",
         info_text="Left-click anywhere to set the extremes of the segment. The points are set on button release.")

tools_2d["tool2d_draw_polylines_radio"] = \
    Tool(obj_name="tool2d_draw_polylines_radio",
         status_text="Drawing lines",
         info_text="Left-click anywhere to set the next vertex of the line. "
                   "\nPress ENTER when the line is complete."
                   "\nPress ESCAPE to stop drawing the line."
                   "\nPress BACKSPACE to delete last drawn vertex."
         )

tools_2d["tool2d_draw_polygons_radio"] = \
    Tool(obj_name="tool2d_draw_polygons_radio",
         status_text="Drawing polygons",
         info_text="Left-click anywhere to set the next vertex of the polygon. "
                   "\nPress ENTER when the polygon is complete."
                   "\nPress ESCAPE to stop drawing the line."
                   "\nPress BACKSPACE to delete last drawn vertex."
         )

tools_2d["tool2d_erase_shapes_radio"] = \
    Tool(obj_name="tool2d_erase_shapes_radio",
         status_text="Erasing shapes",
         info_text="Draw a selection box by pressing the left button of the mouse "
                   "and dragging the mouse. Every shape falling inside the area "
                   "or overlapping it will be erased."
         )

tools_2d["tool2d_select_shapes_radio"] = \
    Tool(obj_name="tool2d_select_shapes_radio",
         status_text="Selecting shapes",
         info_text="Draw a selection box by pressing the left button of the mouse and dragging the mouse."
         )

tools_2d["tool2d_operation_radio"] = \
    Tool(obj_name="tool2d_operation_radio",
         status_text="Performing a geometric operation",
         info_text="Select an operation to perform from the drop-down menu, select a series of shapes "
                   "from the canvas and click the button to start the operation."
         )

tools_2d["tool2d_operation_select"] = \
    Tool(obj_type="select",
         obj_name="tool2d_operation_select",
         items={
             "Count Geometries": Tool(
                 obj_type="select_item",
                 obj_name="op_count_geoms_select_item",
                 status_text="Counting the geometries",
                 info_text="Counts the geometries in the canvas",
                 operation_func=geom_count
             ),
             "Count Half Geometries": Tool(
                 obj_type="select_item",
                 obj_name="op2_select_item",
                 status_text="Computing some other geometric stuff",
                 info_text="Operation 2 does something else",
                 operation_func=geom_count_half
             ),
             "My new supercool operation": Tool(
                 obj_type="select_item",
                 operation_func=my_supercool_new_operation
             ),
             "Point Centroid": Tool(
                 obj_type="select_item",
                 operation_func=points_centroid
             ),
             "Print Geometries": Tool(
                 obj_type="select_item",
                 operation_func=print_geoms
             ),
         }
         )

tools_2d["tool2d_operation_button"] = \
    Tool(obj_type="button",
         obj_name="tool2d_operation_button")

#   configuration of tools_3d
tools_3d = dict()  # will contain config info for all 3d tools

tools_3d["tool3d_insert_shape_select"] = \
    Tool(obj_type="select",
         obj_name="tool3d_insert_shape_select",
         items={}
         )


def add_select_options(**kwargs):
    select = kwargs.pop("select", None)
    if select is not None:
        options = kwargs.pop("options", None)
        if options is not None:
            for opt, func in options:
                select.items[opt] = Tool(obj_type="select_item", operation_func=func)


add_select_options(select=tools_3d["tool3d_insert_shape_select"], options=(("Random Points", ""),
                                                                           ("Cuboid", ""),
                                                                           ("Tetrahedron", "")))

