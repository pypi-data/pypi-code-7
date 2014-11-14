from PySide.QtGui import *
from PySide.QtCore import *
from karmadbg.uicore.async import async
from karmadbg.uicore.basewidgets import BaseTextEdit

class QDisasmView (BaseTextEdit):

    def __init__(self, uimanager, parent = None):
        super(QDisasmView, self).__init__(parent)
        self.uimanager = uimanager
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

    def getVisibleLineCount(self):
        cursor = self.textCursor()
        fontMetric = QFontMetrics( cursor.charFormat().font()) 
        lineHeight = fontMetric.height()
        return self.height() / lineHeight

    def updateView(self):
        lineCount = self.getVisibleLineCount()
        self.firstLineRelPos = -lineCount/2
        self.doUpdateView()

    def clearView(self):
        self.setPlainText("")

    @async
    def doUpdateView(self):

        if not self.isEnabled():
            return

        lineCount = self.getVisibleLineCount()

        disasmLines = yield ( self.uimanager.callFunction(getDisasm, lineCount, self.firstLineRelPos, self.uimanager.debugClient.getCurrentFrame() ) )

        if len(disasmLines) == 0:
             return

        text = "\n".join(disasmLines)

        self.setPlainText(text)

        selectedPos = -self.firstLineRelPos - 1

        if selectedPos > 0 and selectedPos < lineCount:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.NextBlock, QTextCursor.MoveAnchor, selectedPos)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

            blockFormat = QTextBlockFormat()
            blockFormat.setBackground(QColor(self.currentLineBackground))
            cursor.setBlockFormat(blockFormat)
            
            charFormat = QTextCharFormat()
            charFormat.setForeground(QColor(self.currentLineColor))
            cursor.setCharFormat(charFormat)


    def resizeEvent (self, resizeEvent):
        super(QDisasmView, self).resizeEvent(resizeEvent)
        lineCount = self.getVisibleLineCount()
        self.firstLineRelPos = -lineCount/2
        self.doUpdateView()

    def wheelEvent( self, wheelEvent ):
        numDegrees = wheelEvent.delta() / 8
        numSteps = numDegrees / 15
        self.firstLineRelPos =  self.firstLineRelPos - numSteps
        self.doUpdateView()

    def keyPressEvent(self,event):

        lineCount = self.getVisibleLineCount()

        if event.key() == Qt.Key_Up:
            self.firstLineRelPos =  self.firstLineRelPos - 1
            self.doUpdateView()
            return

        if event.key() == Qt.Key_Down:
            self.firstLineRelPos =  self.firstLineRelPos + 1
            self.doUpdateView()
            return

        if event.key() == Qt.Key_PageUp:
            self.firstLineRelPos =  self.firstLineRelPos - lineCount
            self.doUpdateView()
            return

        if event.key() == Qt.Key_PageDown:
            self.firstLineRelPos =  self.firstLineRelPos + lineCount
            self.doUpdateView()
            return

        super(QDisasmView, self).keyPressEvent(event)


class DisasmWidget( QDockWidget ):
    def __init__(self, widgetSettings, uimanager):
        super(DisasmWidget, self).__init__()
        self.uimanager = uimanager
        self.disasmView = QDisasmView(uimanager, parent = self)
        self.setWindowTitle("Disassmbler")
        self.setWidget(self.disasmView )
        self.disasmView.setReadOnly(True)
        self.disasmView.setDisabled(True)

        self.uimanager.targetStopped.connect(self.onTargetStopped)
        self.uimanager.targetDetached.connect(self.onTargetDetached)
        self.uimanager.targetRunning.connect(self.onTargetRunning)
        self.uimanager.targetDataChanged.connect(self.onTargetDataChanged)

        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

    def onTargetStopped(self):
        self.disasmView.setEnabled(True)
        self.disasmView.updateView()

    def onTargetRunning(self):
        self.disasmView.setEnabled(False)
        self.disasmView.updateView()

    def onTargetDetached(self):
        self.disasmView.setEnabled(False)
        self.disasmView.clearView()

    def onTargetDataChanged(self):
        self.disasmView.updateView()

def getDisasm(linecount, relpos = 0, frameno=0):
    import pykd
    dasmLines = []
    stack = pykd.getStack()
    ip = stack[frameno].instructionOffset
    try:
        for i in xrange(linecount):
            dasm = pykd.disasm(ip)
            dasm.jumprel(relpos + i)
            dasmLines.append(dasm.instruction())
        return dasmLines
    except pykd.DbgException:
        return []
