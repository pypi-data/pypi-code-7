
from PySide.QtCore import Qt
from PySide.QtGui import QPlainTextEdit

from karmadbg.uicore.async import async
from karmadbg.uicore.basewidgets import PythonDataViewWidget

class PythonLocalsWidget(PythonDataViewWidget):

    def __init__(self, widgetSettings, uimanager): 
        super(PythonLocalsWidget,self).__init__(uimanager)

        self.uimanager = uimanager

        self.localsView = QPlainTextEdit()
        self.localsView.setReadOnly(True)
        self.localsView.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.setWidget(self.localsView)

        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

    def dataUnavailable(self):
        self.localsView.setPlainText("")

    @async
    def dataUpdate(self):
        localvars= yield( self.uimanager.debugClient.getPythonLocalsAsync() )
        for name, val in localvars.items():
            localvars[name] = val.replace("\n", "\\n")
        self.localsView.setPlainText( reduce(lambda x, y: x + "\n%s: %s" % y, localvars.items(), "") )
