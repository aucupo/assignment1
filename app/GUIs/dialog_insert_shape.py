from app.GUIs._dialog_insert_shape import *
from app.geoms.utils.transformable import *
from PyQt4.QtCore import pyqtSlot, pyqtSignal


class GUI_DialogInsertShape(QtGui.QDialog, Ui_Dialog_insert_shape):
    def __init__(self, parent=None, the_shape=None, canvas=None):
        QtGui.QDialog.__init__(self, parent)
        Ui_Dialog_insert_shape.__init__(self)

        self.canvas = canvas
        self.the_shape = the_shape

        self.setupUi(self)

        self.spin_boxes_sliders_pairs = dict()
        self.init_spin_boxes_sliders_pairs()

        self.__link_spinboxes_to_sliders()

        self.last_position_x = 0.0
        self.last_position_y = 0.0
        self.last_position_z = 0.0

        self.last_rotation_x = 0.0
        self.last_rotation_y = 0.0
        self.last_rotation_z = 0.0

        self.last_scale_x = 1.0
        self.last_scale_y = 1.0
        self.last_scale_z = 1.0

        self.doubleSpinBox_position_x.valueChanged.connect(self.move_shape)
        self.doubleSpinBox_position_y.valueChanged.connect(self.move_shape)
        self.doubleSpinBox_position_z.valueChanged.connect(self.move_shape)
        self.doubleSpinBox_scale_x.valueChanged.connect(self.move_shape)
        self.doubleSpinBox_scale_y.valueChanged.connect(self.move_shape)
        self.doubleSpinBox_scale_z.valueChanged.connect(self.move_shape)
        self.doubleSpinBox_rotation_x.valueChanged.connect(self.move_shape)
        self.doubleSpinBox_rotation_y.valueChanged.connect(self.move_shape)
        self.doubleSpinBox_rotation_z.valueChanged.connect(self.move_shape)

    def init_spin_boxes_sliders_pairs(self):
        spin_boxes = self.findChildren(QtGui.QDoubleSpinBox)
        sliders = self.findChildren(QtGui.QSlider)
        for spin_box in spin_boxes:
            assert isinstance(spin_box, QtGui.QDoubleSpinBox)
            spin_box_name_end = spin_box.objectName()[len("doubleSpinBox"):]
            for slider in sliders:
                assert isinstance(slider, QtGui.QSlider)
                slider_name_end = slider.objectName()[len("horizontalSlider"):]
                if spin_box_name_end == slider_name_end:
                    self.spin_boxes_sliders_pairs[spin_box_name_end] = {"spin_box": spin_box, "slider": slider}

    def __link_spinboxes_to_sliders(self):
        for pair in self.spin_boxes_sliders_pairs.values():
            spin_box, slider = pair["spin_box"], pair["slider"]
            spin_box.valueChanged.connect(self.spinbox_to_slider)
            slider.valueChanged.connect(self.slider_to_spinbox)

    @pyqtSlot(float)
    def spinbox_to_slider(self, value):
        value = int(value*100)
        sending_spin_box = self.sender()
        spin_box_name_end = sending_spin_box.objectName()[len("doubleSpinBox"):]

        paired_slider = self.spin_boxes_sliders_pairs[spin_box_name_end]['slider']
        assert isinstance(paired_slider, QtGui.QSlider)

        if "scale" in paired_slider.objectName():
            if value < 100:
                paired_slider.setValue(int((value - 100) * 100))
            elif value == 100:
                paired_slider.setValue(0)
            else:
                paired_slider.setValue(int(value - 100))
        else:
            paired_slider.setValue(value)

    @pyqtSlot(int)
    def slider_to_spinbox(self, value):
        value = float(format(value/100.0, '.1f'))
        sending_slider = self.sender()
        slider_name_end = sending_slider.objectName()[len("horizontalSlider"):]

        paired_spin_box = self.spin_boxes_sliders_pairs[slider_name_end]['spin_box']
        assert isinstance(paired_spin_box, QtGui.QDoubleSpinBox)

        if "scale" in paired_spin_box.objectName():
            if value < 0:
                paired_spin_box.setValue(value / 100 + 1)
            elif value == 0:
                paired_spin_box.setValue(1)
            else:
                paired_spin_box.setValue(value + 1)
        else:
            paired_spin_box.setValue(value)

    #TODO
    @pyqtSlot(float)
    def move_shape(self, value):
        if isinstance(self.the_shape, Transformable):

            delta_scale = (self.doubleSpinBox_scale_x.value() / self.last_scale_x,
                           self.doubleSpinBox_scale_y.value() / self.last_scale_y,
                           self.doubleSpinBox_scale_z.value() / self.last_scale_z)

            delta_rotation = (self.doubleSpinBox_rotation_x.value() - self.last_rotation_x,
                              self.doubleSpinBox_rotation_y.value() - self.last_rotation_y,
                              self.doubleSpinBox_rotation_z.value() - self.last_rotation_z)

            delta_position = (self.doubleSpinBox_position_x.value() - self.last_position_x,
                              self.doubleSpinBox_position_y.value() - self.last_position_y,
                              self.doubleSpinBox_position_z.value() - self.last_position_z)

            # print("OLD VERTICES:" + str(self.the_shape.world_coords()))
            # print("shape: " + str(self.the_shape.renderable_vertex_array['coords']))
            # print("Matrix: " + str(self.the_shape._model2world_matrix))
            # print("last_x " + str(self.last_position_x))
            # print("delta_x " + str(delta_position[0]) )
            #
            # print("move: \n scale=" + str(delta_scale) + "\n rotation=" + str(delta_rotation) + "\n position=" +  str(delta_position))

            self.the_shape.reset()
            self.the_shape.scale(*delta_scale)
            self.the_shape.apply_transformation()

            self.the_shape.reset()
            self.the_shape.rotate(delta_rotation[0], 1, 0, 0)
            self.the_shape.rotate(delta_rotation[1], 0, 1, 0)
            self.the_shape.rotate(delta_rotation[2], 0, 0, 1)
            self.the_shape.apply_transformation()

            self.the_shape.reset()
            self.the_shape.move(*delta_position)
            self.the_shape.apply_transformation()

            self.the_shape.update_renderable_arrays()

            self.canvas.updateGL()

        self.last_position_x = self.doubleSpinBox_position_x.value()
        self.last_position_y = self.doubleSpinBox_position_y.value()
        self.last_position_z = self.doubleSpinBox_position_z.value()

        self.last_rotation_x = self.doubleSpinBox_rotation_x.value()
        self.last_rotation_y = self.doubleSpinBox_rotation_y.value()
        self.last_rotation_z = self.doubleSpinBox_rotation_z.value()

        self.last_scale_x = self.doubleSpinBox_scale_x.value()
        self.last_scale_y = self.doubleSpinBox_scale_y.value()
        self.last_scale_z = self.doubleSpinBox_scale_z.value()
