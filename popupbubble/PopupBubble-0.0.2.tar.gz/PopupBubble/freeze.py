#!/usr/bin/env python3

import sys
from PySide import QtCore, QtGui

class Dialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        button = QtGui.QPushButton("test")
        layout = QtGui.QVBoxLayout()
        layout.addWidget(button)
        self.setLayout(layout)

app = QtGui.QApplication(sys.argv)
toast = Dialog()
toast.show()
app.exec_()
print("App freezes the main process!")
