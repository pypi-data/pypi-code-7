from PySide.QtCore import QObject

from PySide.QtGui import *
from PySide.QtCore import *

from karmadbg.uicore.async import async
from karmadbg.uicore.basewidgets import BaseTextEdit

class PythonCodeEditor(BaseTextEdit):

    def __init__(self,parent):
        super(PythonCodeEditor,self).__init__(parent)
        self.normalLineFormat = QTextBlockFormat()
        self.normalLineCharFormat = QTextCharFormat()
        self.currentLine=-1
        self.breakpointLines = set()
        self.codecName = ""
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

    def setBlockFormat(self,block,format = QTextBlockFormat(), charformat = QTextCharFormat() ):
        pos = block.position()
        cursor = self.textCursor()
        cursor.setPosition( pos, QTextCursor.MoveAnchor)
        cursor.movePosition( QTextCursor.EndOfBlock, QTextCursor.KeepAnchor )
        cursor.setBlockFormat(format)
        cursor.setCharFormat(charformat)

    def ensureLineVisible(self,lineno):
        block = self.document().findBlockByLineNumber(lineno-1)
        cursor = self.textCursor()
        cursor.setPosition( block.position(), QTextCursor.MoveAnchor)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def setCurrentLine(self,lineno):
        self.resetCurrentLine()
        block = self.document().findBlockByLineNumber(lineno-1)
        self.currentLine = lineno-1
        currentLineFormat = QTextBlockFormat()
        currentLineFormat.setBackground(QColor(self.currentLineBackground))
        currentLineCharFormat = QTextCharFormat()
        currentLineCharFormat.setForeground(QColor(self.currentLineColor))
        self.setBlockFormat( block, currentLineFormat, currentLineCharFormat )
        self.ensureLineVisible(lineno-1)

    def addBreakpointLine(self,lineno):

        lineno = lineno - 1

        self.breakpointLines.add(lineno)

        block = self.document().findBlockByLineNumber(lineno)

        if lineno != self.currentLine:
            bpLineFormat = QTextBlockFormat()
            bpLineFormat.setBackground(QColor(self.bpLineBackground))
            bpLineCharFormat = QTextCharFormat()
            bpLineCharFormat.setForeground(QColor(self.bpLineColor))
            self.setBlockFormat(block, bpLineFormat, bpLineCharFormat )

    def removeBreakpointLine(self,lineno):

        lineno = lineno - 1

        block = self.document().findBlockByLineNumber(lineno)

        if lineno != self.currentLine:
            self.setBlockFormat(block)

        self.breakpointLines.remove(lineno)

    def resetBreakpointLines(self):

        for line in self.breakpointLines:
            block = self.document().findBlockByLineNumber(line)
            self.setBlockFormat(block)
        self.breakpointLines.clear()


    def resetCurrentLine(self):
        if self.currentLine == -1:
            return

        block = self.document().findBlockByLineNumber(self.currentLine)

        if self.currentLine in self.breakpointLines:
            bpLineFormat = QTextBlockFormat()
            bpLineFormat.setBackground(QColor(self.bpLineBackground))
            bpLineCharFormat = QTextCharFormat()
            bpLineCharFormat.setForeground(QColor(self.bpLineColor))
            self.setBlockFormat(block, bpLineFormat, bpLineCharFormat )
        else:
            self.setBlockFormat( block)

        self.currentLine = -1


    def setErrorLine(self,lineno):
        pass

    def contextMenuEvent(self, event):

        def getSeFileEncoding(codecName):
            return lambda : self.setFileEncoding(codecName) 

        menu = self.createStandardContextMenu()
        encodingMenu = menu.addMenu("Encoding")

        codecNames = [codeName.data() for codeName in QTextCodec.availableCodecs()]
        codecNames.sort()

        for codecName in codecNames:
            name = codecName
            action = QAction(codecName, self)
            action.triggered.connect( getSeFileEncoding(codecName) )
            encodingMenu.addAction(action)

        menu.exec_(event.globalPos())

    def setFileEncoding(self,codecName):
        self.codecName = codecName
        self.loadFile(self.fileName)

    def loadFile(self, fileName):

        self.fileName = fileName
        fileContent = ""

        no = 1
        with open(fileName) as f:
            for line in f:
                fileContent += "%-4d|  " % no + line
                no += 1
            #fileContent = reduce( lambda x,y: x + y, file)

        if self.codecName:
            codec = QTextCodec.codecForName(self.codecName)
        else:
            codec = QTextCodec.codecForLocale()

        fileContent = codec.toUnicode(fileContent)
        self.setPlainText(fileContent)


class SourceWidget( QDockWidget ):

    def __init__(self, uimanager, sourceFileName, *args):
        super(SourceWidget, self).__init__(*args)
        self.uimanager = uimanager
        self.mainWnd =uimanager.mainwnd
        self.sourceFileName = sourceFileName
        self.setWindowTitle(self.sourceFileName)
        self.sourceView = PythonCodeEditor(self)
        if self.sourceFileName:
            self.sourceView.loadFile(self.sourceFileName)
        self.setWidget( self.sourceView  )

    def setCurrentLine(self,lineno):
        self.sourceView.setCurrentLine(lineno)

    def addBreakpointLine(self,lineno):
        self.sourceView.addBreakpointLine(lineno)

    def removeBreakpointLine(self, lineno):
        self.sourceView.removeBreakpointLine(lineno)

    def resetCurrentLine(self):
        self.sourceView.resetCurrentLine()

    def setFileName(self,fileName):
        self.sourceFileName = fileName
        self.setWindowTitle(self.sourceFileName)

    def resetBreakpointLines(self):
        self.sourceView.resetBreakpointLines()



class SourceManager(QObject):
    
    def __init__(self, widgetSettings, uimanager):
        QObject.__init__(self)
        self.newDocumentCount = 0
        self.uimanager = uimanager
        self.openTargetSources={}
        self.openPythonSources={}
        self.uimanager.targetStopped.connect(self.onTargetStopped)
        self.uimanager.targetRunning.connect(self.onTargetRunning)
        self.uimanager.targetDetached.connect(self.onTargetDetached)
        self.uimanager.targetDataChanged.connect(self.onTargetDataChanged)

        self.uimanager.pythonStopped.connect(self.onPythonStopped)
        self.uimanager.pythonRunning.connect(self.onPythonRunning)
        self.uimanager.pythonBreakpointAdded.connect(self.onPythonBreakpointAdded)
        self.uimanager.pythonBreakpointRemoved.connect(self.onPythonBreakpointRemoved)
        self.uimanager.pythonExit.connect(self.onPythonExit)

    def onTargetSourceShow(self, fileName, line):

        if fileName=="":
            raise IOError

        if fileName in self.openTargetSources:
            source = self.openTargetSources[fileName]
            source.setVisible(True)
        else:
            source = SourceWidget(self.uimanager, fileName )
            self.openTargetSources[fileName] = source
            self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea,source)

        source.setCurrentLine(line)
        source.raise_()


    def onPythonSourceShow(self, fileName, line):

        if fileName=="":
            return

        if fileName in self.openPythonSources:
            source = self.openPythonSources[fileName]
            source.setVisible(True)
        else:
            try:
                source = SourceWidget(self.uimanager, fileName )
                self.openPythonSources[fileName] = source
                self.uimanager.mainwnd.addDockWidget(Qt.TopDockWidgetArea,source)
            except IOError:
                return

        source.setCurrentLine(line)
        source.raise_()

    @async
    def onTargetStopped(self):
        file, line = yield ( self.uimanager.callFunction( getSourceLine, self.uimanager.debugClient.getCurrentFrame() ) )
        if file != "":
            try:
                self.onTargetSourceShow(file, line)
                return
            except IOError:
                pass

        for source in self.openTargetSources.values():
            source.resetCurrentLine()

    def onTargetDataChanged(self):
        self.onTargetStopped()

    def onTargetRunning(self):
        for source in self.openTargetSources.values():
            source.resetCurrentLine()

    def onTargetDetached(self):
        for source in self.openTargetSources.values():
            source.resetCurrentLine()

    def setVisible(self,visibled):
        pass


    @async
    def onPythonStopped(self):
        file,line = yield( self.uimanager.debugClient.getPythonSourceLineAsync() )
        if file != "":
            self.onPythonSourceShow(file, line)

    def onPythonRunning(self):
        for source in self.openPythonSources.values():
            source.resetCurrentLine()
            
    def onPythonBreakpointAdded(self, filename, lineno):

        if filename in self.openPythonSources:
            source = self.openPythonSources[filename]
            source.addBreakpointLine(lineno)

    def onPythonBreakpointRemoved(self, filename, lineno):
        if filename in self.openPythonSources:
            source = self.openPythonSources[filename]
            source.removeBreakpointLine(lineno)

    def onPythonExit(self):
        for source in self.openPythonSources.values():
            source.resetBreakpointLines()

def getSourceLine(frameno = 0):
    import pykd
    try:
        stack = pykd.getStack()
        ip = stack[frameno].instructionOffset
        fileName, fileLine, displacement = pykd.getSourceLine(ip)
        return (fileName, fileLine)
    except pykd.DbgException:
        return ("", 0)
