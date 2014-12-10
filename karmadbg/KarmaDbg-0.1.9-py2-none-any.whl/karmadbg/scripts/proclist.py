import pykd

def getProcessThreadList():

    procId = pykd.getCurrentProcessId()
    pid = pykd.getProcessSystemID(procId)
    exe = pykd.getCurrentProcessExeName()
    threadNumber = pykd.getNumberThreads()
    threadLst = []
    for t in range(threadNumber):
        threadId = pykd.getThreadId(t)
        #tid = pykd.getThreadSystemID(threadId)
    #    threadLst.append(tid)
    return [ (pid, exe, threadLst, ), ]


if __name__ == "__main__":
    getProcessThreadList()
