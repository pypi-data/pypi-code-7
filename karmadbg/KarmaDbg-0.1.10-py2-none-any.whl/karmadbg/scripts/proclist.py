import pykd

def getProcessThreadList():

    if pykd.isKernelDebugging():
        return []

    procId = pykd.getCurrentProcessId()
    pid = pykd.getProcessSystemID(procId)
    exe = pykd.getCurrentProcessExeName()
    threadNumber = pykd.getNumberThreads()
    threadLst = []
    for t in range(threadNumber):
        threadId = pykd.getThreadId(t)
        tid = pykd.getThreadSystemID(threadId)
        threadLst.append(tid)
    return [ (pid, exe, threadLst, ), ]

def setCurrentThread(tid):
    threadId = pykd.getThreadIdBySystemID(tid)
    pykd.setCurrentThreadId(threadId)


