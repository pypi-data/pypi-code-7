from PySide.QtGui import *
from PySide.QtCore import *

from karmadbg.uicore.async import async
from karmadbg.uicore.basewidgets import BaseTextEdit
from karmadbg.scripts.disasm import getDisasm
from karmadbg.scripts.breakpoint import getBreakpoints
from karmadbg.uicore.basewidgets import NativeDataViewWidget

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

    @async
    def dataUpdate(self, expression):

        if expression:
            self.currentIp = yield(self.uimanager.debugClient.getExpressionAsync(expression) )
            if not self.currentIp:
                self.clearView()
                return
        else:
            frame = yield( self.uimanager.debugClient.getCurrentFrameAsync() )
            self.currentIp = frame[0]

        lineCount = self.getVisibleLineCount()

        self.firstLineRelPos = -lineCount/2

        self.disasmLines = yield ( self.uimanager.debugClient.callFunctionAsync(getDisasm, lineCount, self.firstLineRelPos,  self.currentIp ) )

        if len(self.disasmLines) == 0:
            self.clearView()
            return

        self.breakpointLines = yield (self.uimanager.debugClient.callFunctionAsync(getBreakpoints) )

        text = "\n".join(self.disasmLines)

        self.setPlainText(text)

        self.highlightText()
        
    @async
    def viewUpdate(self):

        lineCount = self.getVisibleLineCount()

        self.firstLineRelPos = -lineCount/2

        self.disasmLines = yield ( self.uimanager.debugClient.callFunctionAsync(getDisasm, lineCount, self.firstLineRelPos, self.currentIp ) )

        if len(self.disasmLines) == 0:
             return

        text = "\n".join(self.disasmLines)

        self.setPlainText(text)

        self.highlightText()


    def clearView(self):

        self.setPlainText("")

        
    def highlightText(self):

        selectedPos = -self.firstLineRelPos - 1
        lineCount = len(self.disasmLines)

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
        if self.isEnabled():
            self.viewUpdate()

    def wheelEvent( self, wheelEvent ):
        numDegrees = wheelEvent.delta() / 8
        numSteps = numDegrees / 15
        self.firstLineRelPos =  self.firstLineRelPos - numSteps
        if self.isEnabled():
            self.viewUpdate()

    def keyPressEvent(self,event):

        lineCount = self.getVisibleLineCount()

        if event.key() == Qt.Key_Up:
            self.firstLineRelPos =  self.firstLineRelPos - 1
            if self.isEnabled():
                self.viewUpdate()
            return

        if event.key() == Qt.Key_Down:
            self.firstLineRelPos =  self.firstLineRelPos + 1
            if self.isEnabled():
                self.viewUpdate()
            return

        if event.key() == Qt.Key_PageUp:
            self.firstLineRelPos =  self.firstLineRelPos - lineCount
            if self.isEnabled():
                self.viewUpdate()
            return

        if event.key() == Qt.Key_PageDown:
            self.firstLineRelPos =  self.firstLineRelPos + lineCount
            if self.isEnabled():
                self.viewUpdate()
            return

        super(QDisasmView, self).keyPressEvent(event)


class DisasmWidget(NativeDataViewWidget):
    def __init__(self, widgetSettings, uimanager):
        super(DisasmWidget, self).__init__(uimanager)
        self.uimanager = uimanager
        self.disasmView = QDisasmView(uimanager, parent = self)
        self.setWindowTitle("Disassmbler")
        self.disasmView.setReadOnly(True)

        self.exprEdit = (QLineEdit())
        self.exprEdit.returnPressed.connect(self.dataUpdate)

        vlayout = QVBoxLayout()
        vlayout.addWidget(self.exprEdit )
        vlayout.addWidget(self.disasmView)
        vlayout.setSpacing(4)
        vlayout.setContentsMargins(4,4,4,4)

        frame = QFrame()
        frame.setLayout(vlayout)

        self.setWidget(frame)
        self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea, self)

    def dataUnavailable(self):
        self.disasmView.clearView()

    def dataUpdate(self):
        self.disasmView.dataUpdate(expression = self.exprEdit.text() )

def getDisasm(linecount, relpos = 0, offset = 0):
    import pykd
    dasmLines = []
    try:
        if offset == 0:
            offset = pykd.cpu().ip
        for i in xrange(linecount):
            dasm = pykd.disasm(pykd.addr64(offset))
            dasm.jumprel(relpos + i)
            dasmLines.append(dasm.instruction())
        return dasmLines
    except pykd.DbgException:
        return []
