from codeop import compile_command

import pykd
from pykd import *

from karmadbg.dbgcore.dbgdecl import *
from karmadbg.dbgcore.util import *
from karmadbg.dbgcore.pydebug import PythonDebugger

class EventMonitor(pykd.eventHandler):

    def __init__(self, debugServer):
        super(EventMonitor,self).__init__()
        self.eventHandler = debugServer.eventHandler
        self.debugServer = debugServer

    def onExecutionStatusChange(self, status):
        event = { 
            pykd.executionStatus.Go : TargetState(TargetState.TARGET_RUNNING),
            pykd.executionStatus.Break : TargetState(TargetState.TARGET_STOPPED),
            pykd.executionStatus.NoDebuggee : TargetState(TargetState.TARGET_DETACHED)
        }[status]

        self.debugServer.currentFrame = 0
        self.eventHandler.onTargetStateChanged(event)

    def onCurrentThreadChange(self, threadId):
        self.eventHandler.onTargetDataChanged()


class NativeDebugger(object):

    def __init__(self, debugServer):
        self.eventHandler = debugServer.getClientEventHandler()
        self.clientOutput = debugServer.getClientOutput()
        self.debugServer = debugServer
        self.currentFrame = 0

        pykd.initialize()

        self.eventMonitor = EventMonitor(self)

    def debugCommand(self, commandStr):

        if self.isNativeCmd(commandStr):
           return self.nativeCmd(commandStr)

        elif self.isWindbgCommand(commandStr):
            return self.windbgCommand(commandStr)
        else:
            return self.pythonCommand(commandStr)
        
    def isNativeCmd(self, commandStr):
        return commandStr in ['g', 'p', 't' ]

    def nativeCmd(self,commandStr):
        try:
            res = { 
                'g' : pykd.go,
                'p' : pykd.step,
                't' : pykd.trace,
            }[commandStr]()
            if res:
                print res
            return MakeResultOk()
        except pykd.DbgException:
            print showexception(sys.exc_info())
            return MakeResultError()

    def isWindbgCommand(self, commandStr):
        return commandStr[0] in ['.', '!', '~', '?', '#', '|', ';', '$']

    def windbgCommand(self, commandStr):
        try:
            res = pykd.dbgCommand(commandStr)
            if res:
                print res
            return MakeResultOk()
        except pykd.DbgException:
            print showtraceback(sys.exc_info())
            return MakeResultError()

    def pythonCommand(self, commandStr):
        try:
            code = compile_command(commandStr, "<input>", "single")
            if code == None:
                return MakeResultNeedMoreData()
        except SyntaxError:
            print showtraceback(sys.exc_info())
            return MakeResultError()

        try:
            exec code in globals()
            return MakeResultOk()

        except SystemExit:
            return MakeResultQuit()

        except:
            print showtraceback(sys.exc_info())
            return MakeResultError()

    def pythonEval(self, expr):
        try:
            return str(eval(expr, globals(), globals()))
        except Exception, e:
            return str(e)

    def getSourceLine(self):
        try:
            stack = getStack()
            ip = stack[0].instructionOffset if len(stack) <= self.currentFrame else stack[self.currentFrame].instructionOffset
            fileName, fileLine, displacement = pykd.getSourceLine(ip)
            return (fileName, fileLine)
        except pykd.DbgException:
            return ("", 0)

    def getDisasm(self,relpos,linecount):
        dasmLines = []
        stack = getStack()
        ip = stack[0].instructionOffset if len(stack) <= self.currentFrame else stack[self.currentFrame].instructionOffset
        try:
            for i in xrange(linecount):
                dasm = pykd.disasm(ip)
                dasm.jumprel(relpos + i)
                dasmLines.append(dasm.instruction())
            return dasmLines
        except pykd.DbgException:
            return []

    def getRegsiters(self):
        return [ r for r in cpu() ]

    def getStackTrace(self):
        try:
            stack = pykd.getStack()
            return [ (frame.frameOffset, frame.returnOffset, pykd.findSymbol(frame.instructionOffset, True) ) for frame in stack ]
        except pykd.DbgException:
            return []

    def getExpr(self,expr):
        try:
            return pykd.expr(expr)
        except pykd.DbgException:
            return None

    def pythonEval(self, expr):
        try:
            return str( eval(expr) )
        except Exception, e:
            return str(e)

    def getMemoryRange(self,addr,length):
        try:
            return pykd.loadBytes(pykd.addr64(addr),length)
        except pykd.MemoryException:
            return None

    def breakin(self):
        try:
            pykd.breakin()
        except pykd.DbgException:
            pass
