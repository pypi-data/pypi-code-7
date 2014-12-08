from PySide.QtGui import QFileDialog, QDialog
from PySide.QtGui import QPushButton, QLineEdit, QHBoxLayout
from PySide.QtCore import Qt

class OpenProcessDialog(QFileDialog):

    def __init__(self,settings,uimanager):
        super(OpenProcessDialog,self).__init__(uimanager.mainwnd)
        self.settings = settings
        self.uimanager = uimanager
        self.setNameFilter( "Executable (*.exe)" )

    def getProcessName(self):
        return self.getOpenFileName()[0]


class OpenDumpDialog(QFileDialog):

    def __init__(self,settings,uimanager):
        super(OpenDumpDialog,self).__init__(uimanager.mainwnd)
        self.settings = settings
        self.uimanager = uimanager

    def getFileName(self):
        return self.getOpenFileName()[0]


class OpenSourceDialog(QFileDialog):

    def __init__(self,settings,uimanager):
        super(OpenSourceDialog,self).__init__(uimanager.mainwnd)
        self.settings = settings
        self.uimanager = uimanager

    def getFileName(self):
        return self.getOpenFileName()[0]

class FindDialog(QDialog):

    def __init__(self, settings, uimanager):
        super(FindDialog,self).__init__(uimanager.mainwnd, Qt.WindowTitleHint)
        self.uimanager = uimanager
        self.findEdit = QLineEdit()
        pushBtn = QPushButton("Find")
        pushBtn.clicked.connect(self.onFindBtn)
        layout =QHBoxLayout()
        layout.addWidget(pushBtn);
        layout.addWidget(self.findEdit);
        self.setLayout(layout)
        self.setTabOrder(self.findEdit, pushBtn)
        self.setWindowTitle("Find")
        self.fromStart = True

    def onFindBtn(self):
        if self.findEdit.text():
            self.uimanager.find(self.findEdit.text(), self.fromStart)
            self.fromStart = False


