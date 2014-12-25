
import pykd

def getDisasm(linecount, relpos = 0, frameno=0):
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

if __name__ == "___main__":
    getDisasm(10)
