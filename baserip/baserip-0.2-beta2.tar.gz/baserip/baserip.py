import sys
from PyQt4 import QtGui
from baserip.ui.br_mainwindow import BR_MainWindow
from baserip.resources import baserip_rc

def run():
    app = QtGui.QApplication(sys.argv)
    MainWindow = BR_MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()
