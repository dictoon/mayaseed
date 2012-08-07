#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PySide import QtGui, QtCore

class RenderSequence_GUI(QtGui.QWidget):
    
    def __init__(self):
        super(RenderSequence_GUI, self).__init__()
        
        self.initUI()
        
    def initUI(self):               
        
    	main_layout = QtGui.QHBoxLayout()
    	self.setLayout(main_layout)



    	src_button = QtGui.QPushButton('src', self)
    	src_button.resize(src_button.sizeHint())
    	src_button.move(40, 10)

    	main_layout.addWidget(src_button)
        
        self.setGeometry(300, 300, 600, 30)
        self.setWindowTitle('appleseed Render Sequence GUI')    
        self.show()
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = RenderSequence_GUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()