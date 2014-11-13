
import sys
import signal
import time
import os

from copy import copy
from multiprocessing import Pipe, Process
from threading import Thread
from abc import abstractmethod
from bdb import BdbQuit

from karmadbg.dbgcore.dbgdecl import *
from karmadbg.dbgcore.nativedbg import NativeDebugger
from karmadbg.dbgcore.pydebug import PythonDebugger
from karmadbg.dbgcore.macro import *
from karmadbg.dbgcore.util import *

class ConsoleDebugClient(AbstractDebugClient):

    def output(self,str):
        sys.stdout.write(str)

    def input(self):
        return sys.stdin.readline()

    def onTargetStateChanged(self,state):
        pass

    def onTargetDataChanged(self):
        pass

    def onPythonStart(self):
        return False

    def onPythonQuit(self):
        pass

    def onPythonStateChange(self,state):
        pass

    def onPythonBreakpointAdd(self, file, line):
        pass

    def onPythonBreakpointRemove(self, file, line):
        pass


class DebugServer(object):

    def startServer(self):

        signal.signal( signal.SIGINT, signal.SIG_IGN)

        self.clientOutput = self.getClientOutput()

        sys.stdin = self
        sys.stdout = self
        #sys.stderr = self

        self.nativeDbg = NativeDebugger(self)
        self.pythonDbg = PythonDebugger(self)

        self.commandServer = self.processServerCommand(self)
        self.interruptServer = self.processServerInterrupt(self)

        self.commandLoop(self.nativeDbg)

    def commandLoop(self, commandHandler):

        while not self.commandServer.stopped :
            methodName, args, kwargs = self.commandServer.getRequest()

            if methodName == 'callFunction':
                try:
                    result = args[0](*args[1:],**kwargs)
                except Exception, ex:
                    result = ex
                self.commandServer.sendAnswer(result)

            elif methodName == 'debugCommand':
                 if commandHandler.debugCommand(*args, **kwargs):
                     return False

            elif methodName == 'quit':
                self.quit()
                self.commandServer.sendAnswer(None)
            else:
                try:
                    if hasattr(self.pythonDbg, methodName):
                        result = getattr(self.pythonDbg, methodName)(*args, **kwargs)
                    else:
                        result = getattr(self.nativeDbg, methodName)(*args, **kwargs)
                except Exception, ex:
                    result = ex
                self.commandServer.sendAnswer(result)

        return True

    def write(self,str):
        self.clientOutput.output(str)

    def readline(self):
        return self.clientOutput.input()

    def flush(self):
        pass

    def breakin(self):
        self.nativeDbg.breakin()

    def quit(self):
        self.interruptServer.stop()
        self.commandServer.stop()

    def isMacroCmd(self,commandStr):
        return commandStr[0] == '%'

    def macroCmd(self,commandStr):

        try:
            vars = commandStr.split()

            if vars[0] == "%run":
                self.runCodeCommand(vars[1:], debug = False)
            elif vars[0] == "%rund":
                self.runCodeCommand(vars[1:], debug = True)
            else:
                macroCommand(commandStr)
                self.commandServer.sendAnswer( MakeResultOk() )

        except SystemExit:
            self.commandServer.sendAnswer( MakeResultQuit() )

        except:
            print showtraceback(sys.exc_info())
            self.commandServer.sendAnswer( MakeResultError() )

    def runCodeCommand(self, vars, debug = False):

        if len(vars) == 0:
            self.commandServer.sendAnswer( MakeResultOk() )
            return

        fileName = vars[0]
        args = vars[1:]

        argv = sys.argv

        try:

            dirname, _ = os.path.split(fileName)

            if not dirname:
                script, suffix = os.path.splitext(fileName)
                _,fileName,desc=imp.find_module(script)
                   
            sys.argv = []
            sys.argv.append(fileName)
            sys.argv.extend(args)

            glob = copy( globals() )
            glob["__name__"] = "__main__"
            glob["__file__"] = fileName

            if debug:
                with self.pythonDbg as pydbg:
                    try:
                        execfile(fileName, glob )
                    except BdbQuit:
                        pass
            else:
                execfile(fileName, glob )

        except:
            sys.stderr.write(showtraceback( sys.exc_info(), 2 ))
            pass

        self.commandServer.sendAnswer( MakeResultOk() )

        sys.argv = argv


    def pythonEval(self, expr):
        try:
            return str( eval(expr) )
        except Exception, e:
            return str(e)


class LocalProxy(object):

    def __init__(self, pipe):
        self.pipe = pipe

    def __getattr__(self, methodname):

        class callToPipe(object):

            def __init__(self,pipe):
                self.pipe=pipe

            def __call__(self, *args, **kwargs):
                self.pipe.send( (methodname, args, kwargs) )
                result = self.pipe.recv()
                if isinstance(result, Exception):
                    raise result
                return result

        return callToPipe(self.pipe)


class LocalStub(object):

    def __init__(self, pipe, requestHandler):
        self.pipe = pipe
        self.requestHandler = requestHandler
        self.stopped = False

    def getRequest(self):
        return self.pipe.recv()

    def sendAnswer(self, answer):
        return self.pipe.send(answer)

    def stop(self):
        self.stopped = True

class LocalThreadApartmentStub(LocalStub):

    def __init__(self, pipe, requestHandler):
        super(LocalThreadApartmentStub,self).__init__(pipe,requestHandler)
        self.workThread = Thread(target=self.threadRoutine)
        self.workThread.start()

    def threadRoutine(self):

        while not self.stopped:
            if self.pipe.poll(1):
                methodName, args, kwargs = self.getRequest()
                try:
                    result = getattr(self.requestHandler, methodName)(*args, **kwargs)
                except Exception, ex:
                    result = ex
                self.sendAnswer(result)

    def stop(self):
        self.stopped = True
        self.workThread.join()


class LocalDebugServer(DebugServer,Process):

    def __init__(self):
        self.outputPipe, outputServerPipe = Pipe()
        self.commandPipe, commandServerPipe = Pipe()
        self.interruptPipe, interruptServerPipe = Pipe()
        self.eventPipe, eventServerPipe = Pipe()
        self.outputStub = None
        self.eventStub = None
        self.interruptStub = None
        self.commadStub = None
        self.stopped = False

        DebugServer.__init__(self)
        Process.__init__(self, target = self.processRoutine, args = (outputServerPipe, commandServerPipe, interruptServerPipe, eventServerPipe))

    def processRoutine(self, outputPipe, commandPipe, interruptPipe, eventPipe ):

        self.outputPipe = outputPipe
        self.commandPipe = commandPipe
        self.interruptPipe = interruptPipe
        self.eventPipe = eventPipe

        self.startServer()

    def getClientOutput(self):
        return LocalProxy(self.outputPipe)

    def getClientEventHandler(self):
        return LocalProxy(self.eventPipe) 

    def getServerControl(self):
        return LocalProxy(self.commandPipe)

    def getServerInterrupt(self):
        return LocalProxy(self.interruptPipe)

    def processClientOutput(self, requestHandler):
        if not self.outputStub:
            self.outputStub  = LocalThreadApartmentStub(self.outputPipe, requestHandler)
        return self.outputStub

    def processClientEvents(self, requestHandler):
        if not self.eventStub:
            self.eventStub = LocalThreadApartmentStub(self.eventPipe, requestHandler)
        return self.eventStub

    def processServerInterrupt(self, requestHandler):
        if not self.interruptStub:
            self.interruptStub = LocalThreadApartmentStub( self.interruptPipe, requestHandler)
        return self.interruptStub

    def processServerCommand(self, requestHandler):
        if not self.commadStub:
            self.commandStub = LocalStub(self.commandPipe, requestHandler)
        return self.commandStub
        


class DbgEngine(object):
    
    def __init__(self, dbgClient, dbgServer, dbgSettings):
        self.dbgServer = dbgServer
        self.dbgClient = dbgClient
        self.dbgSettings = dbgSettings

    def start(self):
        #start server
        self.dbgServer.start()

        #start client callback thread-apartment handlers
        self.outputStub = self.dbgServer.processClientOutput(self.dbgClient)
        self.eventsStub = self.dbgServer.processClientEvents(self.dbgClient)

        #init script
        ctrl = self.dbgServer.getServerControl()
        output = self.dbgServer.getClientOutput()
        if len(self.dbgSettings.dbgEngExtensions) > 0:
            ctrl.debugCommand("print \"\"")
            ctrl.debugCommand("print \"loading DbgEng extensions:\"")
            for ext in self.dbgSettings.dbgEngExtensions:
                if ext.startup:
                    ctrl.debugCommand(".load %s" % ext.path, echo=True)
            ctrl.debugCommand("print \"\"")

    def stop(self):

        #stop debug server
        self.dbgServer.getServerInterrupt().breakin()
        self.dbgServer.getServerControl().quit()

        #stop client callback thread-apartment handlers
        self.outputStub.stop()
        self.eventsStub.stop()
        
    def getServer(self):
        return self.dbgServer

    def getClient(self):
        return self.dbgClient
