
from PySide.QtCore import *

from karmadbg.dbgcore.dbgengine import DbgEngine, LocalDebugServer
from karmadbg.uicore.async import AsyncOperation, async

import time


class DebugAsyncCall(QRunnable):

    def __init__(self, dbgclient, *args, **kwargs):
        super(DebugAsyncCall,self).__init__()
        self.dbgclient = dbgclient
        self.asyncmgr = dbgclient.asyncMgr
        self.args = args
        self.kwargs = kwargs

    def doTaskAsync(self,async):

        class AsyncSignals(QObject):
            asyncDone = Signal(object)

        def onAsyncDone(res):
            try:
                asyncOp = async.send(res[0])
                asyncOp.doTaskAsync(async)
            except StopIteration:
                pass

        self.signals = AsyncSignals()
        self.signals.asyncDone.connect(onAsyncDone)
        self.asyncmgr.asyncCall(self)

    def run(self):
        res = self.task(*self.args, **self.kwargs)
        self.signals.asyncDone.emit((res,))

    def task(self, *args, **kwargs):
        pass


class AsyncCallManager(QThreadPool):

    def __init__(self):
        super(AsyncCallManager,self).__init__()
        self.setMaxThreadCount(1)

    def asyncCall(self, task):
        self.start(task)

    def stop(self):
        self.waitForDone()


class InputWaiterSync(QObject):

    def __init__(self):
        self.inputMutex = QMutex()
        self.inputCompleted = QWaitCondition()
        self.inputBuffer = ""
        self.inputMutex.lock()

    def inputComplete(self,str):
        self.inputMutex.lock()
        self.inputBuffer = str
        self.inputCompleted.wakeAll()
        self.inputMutex.unlock()
            
    def wait(self):
        self.inputCompleted.wait(self.inputMutex)
        self.inputMutex.unlock()
        return self.inputBuffer


class DebugClient(QObject):

    inputCompleted = Signal(str)

    def __init__(self, uimanager, dbgsettings):

        super(DebugClient,self).__init__()
        self.uimanager = uimanager

        self.activePythonDbg = False

        self.dbgServer = LocalDebugServer()
        self.dbgEngine = DbgEngine(self, self.dbgServer, dbgsettings)

        self.serverControl = self.dbgServer.getServerControl()
        self.serverInterrupt = self.dbgServer.getServerInterrupt()

        self.asyncMgr = AsyncCallManager()

        self.inputCompleted.connect(self.inputComplete)

        self.inputWaiter = None
        self.inputBuffer = ""
        
        self.currentFrame = 0
    


    def start(self):
        self.uimanager.outputRequired.emit("KarmaDbg UI client. Version 0.0.0\n")
        self.dbgEngine.start()
        self.callCommand("", echo=False)

    def stop(self):
        self.dbgEngine.stop()
        self.asyncMgr.stop()

    def inputComplete(self,str):
        if self.inputWaiter:
            self.inputWaiter.inputComplete(str)
            return
        self.callCommand(str)

    @async
    def callCommand(self,str, echo=True):

        class CallCommandAsync(DebugAsyncCall):

            def task(self,cmdstr):
                return self.dbgclient.serverControl.debugCommand(cmdstr)

        if echo:
            self.uimanager.outputRequired.emit(str + "\n")

        self.uimanager.inputCompleted.emit()
 
        if str == "":
            str = "\n"

        if self.inputBuffer == "":
            self.inputBuffer = str
        else:
            self.inputBuffer += "\n" + str

        result = yield( CallCommandAsync(self, self.inputBuffer) )
           
        if result.IsQuit:
           self.uimanager.quit()

        if result.IsNeedMoreData:
            self.uimanager.outputRequired.emit("...")
        else:
            self.inputBuffer = ""
            if self.activePythonDbg:
                self.uimanager.outputRequired.emit("PY>")
            else:
                self.uimanager.outputRequired.emit(">>>")

        self.uimanager.inputRequired.emit()

    def output(self,str):
        self.uimanager.outputRequired.emit(str)

    def input(self):
        self.inputWaiter = InputWaiterSync()
        self.uimanager.inputRequired.emit()
        str = self.inputWaiter.wait()
        self.uimanager.inputCompleted.emit()
        self.uimanager.outputRequired.emit(str + "\n")
        self.inputWaiter = None
        return str

    def setCurrentFrame(self, frameno):
        self.currentFrame = frameno
        self.uimanager.targetDataChanged.emit()

    def getCurrentFrame(self):
        return self.currentFrame
    
    def onTargetStateChanged(self,state):
        self.currentFrame = 0
        if state.IsRunning:
            self.uimanager.targetRunning.emit()
        elif state.IsStopped:
            self.uimanager.targetStopped.emit()
        elif state.IsNoTarget:
            self.uimanager.targetDetached.emit()

    def onTargetDataChanged(self):
        self.uimanager.taragetDataChanged.emit()

    def openProcess(self, processName):
        cmd = "startProcess(\"" +  processName + "\")"
        self.callCommand(cmd)

    def openDump(self,dumpName):
        cmd="loadDump(\"" + dumpName + "\")"
        self.callCommand(cmd)

    def go(self):
        self.callCommand("g")

    def step(self):
        self.callCommand("p")

    def trace(self):
        self.callCommand("t")

    def breakin(self):
        self.serverInterrupt.breakin()

    def getSourceLineAsync(self):

        class SourceLineAsync(DebugAsyncCall):

            def task(self):
                return self.dbgclient.serverControl.getSourceLine()

        return SourceLineAsync(self)


    def getDisasmAsync(self, relpos, linecount):

        class DisasmAsync(DebugAsyncCall):

            def task(self):
                return self.dbgclient.serverControl.getDisasm(relpos, linecount)

        return DisasmAsync(self)


    def getRegistersAsync(self):

        class RegisterAsync(DebugAsyncCall):

            def task(self):
                return self.dbgclient.serverControl.getRegsiters()
    
        return RegisterAsync(self)

    def getStackTraceAsync(self):

        class StackTraceAsync(DebugAsyncCall):

            def task(self):
                return self.dbgclient.serverControl.getStackTrace()

        return StackTraceAsync(self)

    def getPythonSourceLineAsync(self):

        class PythonSourceLineAsync(DebugAsyncCall):

            def task(self):
                return self.dbgclient.serverControl.getPythonSourceLine()

        return PythonSourceLineAsync(self)

    def getPythonStackTraceAsync(self):

        class PythonStackTraceAsync(DebugAsyncCall):

            def task(self):
                return self.dbgclient.serverControl.getPythonStackTrace()

        return PythonStackTraceAsync(self)

    def getPythonBreakpointListAsync(self):

        class PythonBreakpointListAsync(DebugAsyncCall):

            def task(self):
                return self.dbgclient.serverControl.getPythonBreakpointList()

        return PythonBreakpointListAsync(self)

    def getPythonLocalsAsync(self):

        class PythonLocalsAsync(DebugAsyncCall):

            def task(self):
                return self.dbgclient.serverControl.getPythonLocals()

        return PythonLocalsAsync(self)


    def setCurrentFrameAsync(self, frameno):

        class CurrentFrameAsync(DebugAsyncCall):

            def task(self):
                return self.dbgclient.serverControl.setCurrentFrame(frameno)

        return CurrentFrameAsync(self)

    def getExpressionAsync(self, expr):

        class ExpressionAsync(DebugAsyncCall):

            def task(self):
                return self.dbgclient.serverControl.getExpr(expr)

        return ExpressionAsync(self)

    def getMemoryAsync(self,addr,length):

        class MemoryAsync(DebugAsyncCall):

            def task(self):
                return self.dbgclient.serverControl.getMemoryRange(addr,length)

        return MemoryAsync(self)

    def pythonEvalAsync(self, expr):

        class PythonEvalAsync(DebugAsyncCall):

            def task(self):
                return self.dbgclient.serverControl.pythonEval(expr)

        return PythonEvalAsync(self)

    @async
    def addBreakpoint(self,filename,lineno):

        class AddBreakpointAsync(DebugAsyncCall):
            def task(self):
                return self.dbgclient.serverControl.addBreakpoint(filename,lineno)

        yield (AddBreakpointAsync(self))

    @async
    def removeBreakpoint(self,filename,lineno):

        class RemoveBreakpointAsync(DebugAsyncCall):
            def task(self):
                return self.dbgclient.serverControl.removeBreakpoint(filename,lineno)

        yield (RemoveBreakpointAsync(self))

    def callFunction(self, *args, **kwargs):

        class CallFunctionAsync(DebugAsyncCall):

            def task(self):
                return self.dbgclient.serverControl.callFunction(*args, **kwargs)

        return CallFunctionAsync(self)

    def onPythonStart(self):
        self.activePythonDbg = True
        return True
        #return False

    def onPythonStateChanged(self, state):
        if state.IsRunning:
            self.uimanager.pythonRunning.emit()
        elif state.IsStopped:
            self.uimanager.pythonStopped.emit()

    def onPythonQuit(self):
        self.uimanager.pythonExit.emit()
        self.activePythonDbg = False
        
    def onPythonBreakpointAdd(self, filename, lineno):
        self.uimanager.pythonBreakpointAdded.emit(filename, lineno)

    def onPythonBreakpointRemove(self, filename, lineno):
        self.uimanager.pythonBreakpointRemoved.emit(filename, lineno)

