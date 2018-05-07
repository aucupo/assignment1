from app.GUIs._dialog_random_points import *
from PyQt4.QtCore import pyqtSlot, pyqtSignal


class GUI_DialogRandomPoints(QtGui.QDialog, Ui_Dialog_random_points):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        Ui_Dialog_random_points.__init__(self)

        self.setupUi(self)

        self.__link_spinboxs_to_sliders()
        self.__enable_bbox_integrity()

    def __link_spinboxs_to_sliders(self):
        spin_boxes = self.findChildren(QtGui.QSpinBox)
        sliders = self.findChildren(QtGui.QSlider)

        for spin_box in spin_boxes:
            assert isinstance(spin_box, QtGui.QSpinBox)
            spin_box_name_end = spin_box.objectName()[len("spinBox"):]
            for slider in sliders:
                assert isinstance(slider, QtGui.QSlider)
                slider_name_end = slider.objectName()[len("horizontalSlider"):]
                if spin_box_name_end == slider_name_end:
                    # connect spinbox and slider by name-coupling
                    spin_box.valueChanged.connect(slider.setValue)
                    slider.valueChanged.connect(spin_box.setValue)

    def __enable_bbox_integrity(self):
        # make sure that the max values are always at least one unit bigger than the min values
        self.spinBox_random_points_min_x.valueChanged.connect(self.ensure_bbox_integrity_min)
        self.spinBox_random_points_max_x.valueChanged.connect(self.ensure_bbox_integrity_max)

        # make sure that the max values are always at least one unit bigger than the min values
        self.spinBox_random_points_min_y.valueChanged.connect(self.ensure_bbox_integrity_min)
        self.spinBox_random_points_max_y.valueChanged.connect(self.ensure_bbox_integrity_max)

        # make sure that the max values are always at least one unit bigger than the min values
        self.spinBox_random_points_min_z.valueChanged.connect(self.ensure_bbox_integrity_min)
        self.spinBox_random_points_max_z.valueChanged.connect(self.ensure_bbox_integrity_max)

    @pyqtSlot(int)
    def ensure_bbox_integrity_min(self, value):
        for max_coord, min_coord in ((self.spinBox_random_points_max_x, self.spinBox_random_points_min_x),
                                 (self.spinBox_random_points_max_y, self.spinBox_random_points_min_y),
                                 (self.spinBox_random_points_max_z, self.spinBox_random_points_min_z)):
            if min_coord.value() >= max_coord.value():
                # if the max did not reach yet the maximum possible value, augment the max by 1
                if max_coord.value() < max_coord.maximum():
                    max_coord.setValue(min_coord.value() + 1)
                # otherwise, reduce the min by 1
                else:
                    min_coord.setValue(max_coord.value() - 1)

    @pyqtSlot(int)
    def ensure_bbox_integrity_max(self, value):
        for max_coord, min_coord in ((self.spinBox_random_points_max_x, self.spinBox_random_points_min_x),
                                 (self.spinBox_random_points_max_y, self.spinBox_random_points_min_y),
                                 (self.spinBox_random_points_max_z, self.spinBox_random_points_min_z)):
            if max_coord.value() <= min_coord.value():
                # if the min did not reach yet the minimum possible value, reduce the min by 1
                if min_coord.value() > min_coord.minimum():
                    min_coord.setValue(max_coord.value() - 1)
                # otherwise, augment the max by 1
                else:
                    max_coord.setValue(min_coord.value() + 1)
