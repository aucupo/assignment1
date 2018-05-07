from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSlot
import sys
import sip
from app.canvas3d import *
from PyQt4.QtGui import QActionGroup
from PyQt4.QtCore import QRegExp

import app.GUIs.main_window as main_window
from app.GUIs.dialog_random_points import *
from app.GUIs.dialog_insert_shape import *


class DrawingApp(QtGui.QMainWindow, main_window.Ui_MainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        main_window.Ui_MainWindow.__init__(self)

        self.setupUi(self)

        self.setup_select_items()

        self.tool2d_button_group = QtGui.QButtonGroup()
        self.tool3d_button_group = QtGui.QButtonGroup()

        # self.tool2d_draw_radios = self.tab_2d.findChildren(QtGui.QRadioButton, QRegExp("tool2d_draw.*"))
        # self.tool3d_radios = self.tab_3d.findChildren(QtGui.QRadioButton)
        #
        # for tool in self.tool2d_draw_radios:
        #     print(tool.objectName())

        self.init_actions()
        self.init_info_box()
        self.init_console()

    def init_info_box(self):
        self.info_box.setReadOnly(True)

    def set_info_box_text(self, text):
        self.info_box.setPlainText(text)

    def init_console(self):
        self.console.setReadOnly(True)
        self.console.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)

        font = self.console.font()
        font.setFamily("Courier")
        font.setPointSize(14)
        self.console.setFont(font)

    def console_add_line(self, line):
        self.console.moveCursor(QtGui.QTextCursor.End)

        self.console.insertPlainText("\n" + str(line))

        sb = self.console.verticalScrollBar()
        sb.setValue(sb.maximum())

    def update_status_bar(self, line):
        self.statusbar.showMessage(line)

    def setup_select_items(self):
        """add items to combo boxes in the interface, as described in the config file"""

        from app.config.geom_tools import (
            tools_2d,
            tools_3d
        )
        for tools in (tools_2d, tools_3d):
            for entry in tools.values():
                if entry.obj_type and entry.obj_type == "select":
                    import collections
                    entry.items = collections.OrderedDict(sorted(entry.items.items()))
                    if entry.items:
                        combo_box = self.findChild(QtGui.QComboBox, entry.obj_name)
                        for label in entry.items:
                            combo_box.addItem(label)

    def init_actions(self):
        """
        here we do extra setup for the window (mainly connect signals and slots)
        """

        # group action2D and action3D to make them mutually exclusive
        view_group = QActionGroup(self)
        view_group.addAction(self.action2D)
        view_group.addAction(self.action3D)
        # set 2D view by default
        self.action2D.setChecked(True)
        # connect view (re)set actions to functions
        self.action2D.toggled.connect(self.canvas.reset_view_2d)
        self.action3D.toggled.connect(self.canvas.reset_view_3d)
        self.actionReset.triggered.connect(self.canvas.reset_view)

        self.tool2d_explore_radio.toggled.connect(self.canvas.set_mode_explore)

        for radio2d in self.tab_2d.findChildren(QtGui.QRadioButton, QRegExp("tool2d.*")):
            self.tool2d_button_group.addButton(radio2d)
            radio2d.toggled.connect(self.tool2d_radio_toggled)

        # TODO: do the same for 3dtool buttons

        self.tool2d_operation_button.clicked.connect(self.perform_operation)

        self.tool3d_insert_shape_button.clicked.connect(self.open_insert_3d_shape_dialog)

    @pyqtSlot()
    def open_insert_3d_shape_dialog(self):
        which_shape = self.tool3d_insert_shape_select.currentText()
        if which_shape == "Random Points":
            self.open_insert_random_points_dialog()
        elif which_shape in ("Cuboid", "Tetrahedron"):
            self.open_insert_shape_dialog(which_shape)

    def open_insert_shape_dialog(self, which_shape):
        if which_shape == "Cuboid":
            from app.geoms.cube import Cube
            shape = Cube()
        elif which_shape == "Tetrahedron":
            from app.geoms.tetrahedron import Tetrahedron
            shape = Tetrahedron()

        self.canvas.add_geometry(shape)
        d = GUI_DialogInsertShape(parent=self, the_shape=shape, canvas=self.canvas)
        if d.exec_():
            x = d.doubleSpinBox_position_x
        else:
            self.canvas.remove_geometry(shape)

    def open_insert_random_points_dialog(self):
        d = GUI_DialogRandomPoints(self)
        if d.exec_():
            points_num = d.spinBox_random_points_points_num.value()
            bbox_min_x = d.spinBox_random_points_min_x.value()
            bbox_max_x = d.spinBox_random_points_max_x.value()
            bbox_min_y = d.spinBox_random_points_min_y.value()
            bbox_max_y = d.spinBox_random_points_max_y.value()
            bbox_min_z = d.spinBox_random_points_min_z.value()
            bbox_max_z = d.spinBox_random_points_max_z.value()

            bbox = Box3D(Point3(bbox_min_x, bbox_min_y, bbox_min_z), Point3(bbox_max_x, bbox_max_y, bbox_max_z))

            random_points = Point3.random(bbox, points_num)

            self.canvas.add_geometry(*random_points)

    @pyqtSlot()
    def perform_operation(self):
        from app.config.geom_tools import tools_2d
        if self.tool2d_button_group.checkedButton().objectName() == "tool2d_operation_radio":
            geoms = self.canvas.renderables3d if not self.canvas.selected_geoms else self.canvas.selected_geoms
            self.console_add_line(
                str(
                    tools_2d['tool2d_operation_select'].
                    items[self.tool2d_operation_select.currentText()].
                    operation_func(geoms, self.canvas)
                )
            )

    @pyqtSlot(bool)
    def tool2d_radio_toggled(self, checked):
        if checked:
            from app.config.geom_tools import tools_2d

            btn_name = self.tool2d_button_group.checkedButton().objectName()

            if btn_name == "tool2d_explore_radio":
                self.canvas.set_mode_explore(checked)
            elif btn_name == "tool2d_draw_points_radio":
                self.canvas.set_mode_draw_points(checked)
            elif btn_name == "tool2d_draw_segments_radio":
                self.canvas.set_mode_draw_segments(checked)
            elif btn_name == "tool2d_draw_polygons_radio":
                self.canvas.set_mode_draw_polygons(checked)
            elif btn_name == "tool2d_draw_polylines_radio":
                self.canvas.set_mode_draw_polylines(checked)
            elif btn_name == "tool2d_erase_shapes_radio":
                self.canvas.set_mode_erase(checked)
            elif btn_name == "tool2d_select_shapes_radio":
                self.canvas.set_mode_select(checked)
            elif btn_name == "tool2d_operation_radio":
                self.canvas.set_mode_operation(checked)

            self.set_info_box_text(tools_2d[btn_name].info_text)


def main():
    app = QtGui.QApplication(sys.argv)
    win = DrawingApp()
    win.show()
    app.exec_()


if __name__ == '__main__':
    main()
