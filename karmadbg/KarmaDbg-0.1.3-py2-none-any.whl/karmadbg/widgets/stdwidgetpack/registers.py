
from PySide.QtGui import *
from PySide.QtCore import *
from karmadbg.uicore.async import async

class QRegistersView(QPlainTextEdit):

    def __init__(self, uimanager, parent = None):
        super(QRegistersView, self).__init__(parent)
        self.uimanager = uimanager
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff);
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);

    @async
    def updateView(self):
        regs = yield ( self.uimanager.debugClient.getRegistersAsync() )
        regstxt = ""
        for regName, regValue in regs:
            regstxt += "%s: %d (%x)\n" % (regName, regValue, regValue)
        self.setPlainText(regstxt)


class RegistersWidget(QDockWidget):

    def __init__(self, widgetSettings, uimanager):
        super(RegistersWidget, self).__init__()
        self.uimanager = uimanager
        self.registerView = QRegistersView(uimanager, parent = self)
        self.setWindowTitle("Registers")
        self.setWidget(self.registerView )
        self.registerView.setReadOnly(True)
        self.registerView.setDisabled(True)

        self.uimanager.targetStopped.connect(self.onTargetStopped)
        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

    def onTargetStopped(self):
        self.registerView.setEnabled(True)
        self.registerView.updateView()
