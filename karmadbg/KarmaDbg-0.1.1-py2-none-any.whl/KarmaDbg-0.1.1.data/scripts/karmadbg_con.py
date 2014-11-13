import sys
import os
import time

from threading import Thread

from karmadbg.dbgcore.settings import DbgSettings
from karmadbg.dbgcore.dbgengine import DbgEngine, ConsoleDebugClient, LocalDebugServer


def dbgLoop(dbgEngine):

    dbgControl = dbgEngine.getServer().getServerControl()

    while True:

        inputStr = raw_input(">>>")
        
        while True:

            result = dbgControl.debugCommand( inputStr )

            if result.IsNeedMoreData:
                s = raw_input("...")
                if s == "":
                    s = "\n"
                inputStr += s
                continue

            if result.IsQuit:
                print "stop debugger"
                dbgEngine.stop()
                return

            break

def main():

    import karmadbg
    dirname = os.path.dirname(karmadbg.__file__)
    filename = os.path.join( dirname, "settings", "default.xml" )
    dbgsettings = DbgSettings(filename)

    dbgClient = ConsoleDebugClient()
    dbgServer = LocalDebugServer()

    dbgEngine = DbgEngine( dbgClient, dbgServer, dbgsettings.workspaces[0] )

    dbgEngine.start();

    thread = Thread(target=dbgLoop, args=(dbgEngine,) )
    thread.start()

    while True:
        try:
            thread.join(1000000)
            break
        except KeyboardInterrupt:
            dbgEngine.getServer().getServerInterrupt().breakin()

    thread.join()


if __name__ == "__main__":
    main()

