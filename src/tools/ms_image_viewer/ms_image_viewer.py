import sys
import os
import inspect

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *


SCRIPT_DIR = os.path.split(inspect.getfile(inspect.currentframe()))[0]
sys.path.append(os.path.join(SCRIPT_DIR, 'src'))
sys.path.append(SCRIPT_DIR)

def setFrameSize(label, frame, image):
    width = image.width()
    height = image.height()
    label.setMinimumWidth(width)
    label.setMaximumWidth(width)
    label.setMinimumHeight(height)
    label.setMaximumHeight(height)
    frame.setMinimumWidth(width)
    frame.setMaximumWidth(width)
    frame.setMinimumHeight(height)
    frame.setMaximumHeight(height)

class MainWindow:
    def __init__(self):

        #Initialization of UI Loader class
        loader = QUiLoader()
        file = QFile(os.path.join(SCRIPT_DIR,'ms_image_viewer.ui'))
        file.open(QFile.ReadOnly) 
        self.ui = loader.load(file)   
        file.close()

        #render image
        self.render_image = QImage(600, 400, QImage.Format_ARGB32)
        self.render_image.fill(qRgb(255,0,0))

        #file image
        self.file_image = QImage(600, 400, QImage.Format_ARGB32)
        self.file_image.fill(qRgb(0,255,0))
        self.mem_images = [False, False, False]   # memory images

        self.A_image = self.render_image
        self.B_image = self.file_image

        self.ui.A_label.setPixmap(QPixmap.fromImage(self.A_image))
        setFrameSize(self.ui.A_label, self.ui.A_frame, self.A_image)

        self.ui.B_label.setPixmap(QPixmap.fromImage(self.B_image))
        setFrameSize(self.ui.B_label, self.ui.B_frame, self.B_image)

        self.set_ab()

        #define connectoins
        self.ui.load_button.clicked.connect(self.loadImage)
        self.ui.M1_button.clicked.connect(self.set_mem1_image)
        self.ui.M2_button.clicked.connect(self.set_mem2_image)
        self.ui.M3_button.clicked.connect(self.set_mem3_image)

        self.ui.A_button_grp.buttonClicked.connect(self.setAImage)
        self.ui.B_button_grp.buttonClicked.connect(self.setBImage)


        self.ui.AB_slider.valueChanged.connect(self.set_ab)


    def __del__ (self):
        self.ui = None;

    def setAImage(self):
        if self.ui.A_button_grp.checkedButton().objectName() == 'F_A_radio':
            self.A_image = self.file_image
        elif self.ui.A_button_grp.checkedButton().objectName() == 'R_A_radio':
            self.A_image = self.render_image
        elif self.ui.A_button_grp.checkedButton().objectName() == 'M1_A_radio':
            self.A_image = self.mem_images[0]
        elif self.ui.A_button_grp.checkedButton().objectName() == 'M2_A_radio':
            self.A_image = self.mem_images[1]
        elif self.ui.A_button_grp.checkedButton().objectName() == 'M3_A_radio':
            self.A_image = self.mem_images[2]
        
        self.ui.A_label.setPixmap(QPixmap.fromImage(self.A_image))
        setFrameSize(self.ui.A_label, self.ui.A_frame, self.A_image)
        self.ui.image_frame.setMinimumWidth(self.A_image.width())
        self.ui.image_frame.setMaximumWidth(self.A_image.width())
        self.ui.image_frame.setMinimumHeight(self.A_image.height())
        self.ui.image_frame.setMaximumHeight(self.A_image.height())


    def setBImage(self):
        if self.ui.B_button_grp.checkedButton().objectName() == 'F_B_radio':
            self.B_image = self.file_image
        elif self.ui.B_button_grp.checkedButton().objectName() == 'R_B_radio':
            self.B_image = self.render_image
        elif self.ui.B_button_grp.checkedButton().objectName() == 'M1_B_radio':
            self.B_image = self.mem_images[0]
        elif self.ui.B_button_grp.checkedButton().objectName() == 'M2_B_radio':
            self.B_image = self.mem_images[1]
        elif self.ui.B_button_grp.checkedButton().objectName() == 'M3_B_radio':
            self.B_image = self.mem_images[2]
        self.ui.B_label.setPixmap(QPixmap.fromImage(self.B_image))
        setFrameSize(self.ui.B_label, self.ui.B_frame, self.B_image)


    def loadImage(self):
        image_path = QFileDialog.getOpenFileName()[0]
        self.file_image.load(image_path)

    def set_mem1_image(self):
        if self.ui.AB_slider.value() > 50:
            self.mem_images[0] = QImage.copy(self.A_image)
        else:
            self.mem_images[0] = QImage.copy(self.B_image)

    def set_mem2_image(self):
        if self.ui.AB_slider.value() > 50:
            self.mem_images[1] = QImage.copy(self.A_image)
        else:
            self.mem_images[1] = QImage.copy(self.B_image)

    def set_mem3_image(self):
        if self.ui.AB_slider.value() > 50:
            self.mem_images[2] = QImage.copy(self.A_image)
        else:
            self.mem_images[2] = QImage.copy(self.B_image)

    def set_ab(self):
        slider_value = self.ui.AB_slider.value()
        print slider_value
        if slider_value == 0:
            self.ui.A_frame.hide()
        else:
            self.ui.A_frame.show()
            A_scale_value = (self.A_image.width() / 100.0) * float(slider_value)
            print 'image witdth', self.A_image.width()
            print 'width', self.A_image.width()
            print 'size', (self.A_image.width() / 100.0) * float(slider_value)
            self.ui.A_frame.setMinimumWidth(A_scale_value)
            self.ui.A_frame.setMaximumWidth(A_scale_value)

    def show(self):
        self.ui.show();








if __name__ == '__main__':

    # create application
    app = QApplication(sys.argv)
    app.setApplicationName('ms_Image_Viewer')

    # create widget
    w = MainWindow();
    w.show();

    # connection
    QObject.connect(app, SIGNAL('lastWindowClosed()'), app, SLOT('quit()'))

    # execute application
    sys.exit(app.exec_())