"""
Interactive session recording.
"""

from __future__ import print_function

import re
import sys
import fileinput
from six import StringIO

try:
    import pexpect
except ImportError:
    print("You need to install the pexpect module to generate session")
    print("output.  This also implies using a system that supports it")
    print("(i.e., not Windows).")
    sys.exit(99)


class CmdSession(object):
    def __init__(self, program, prompt):
        self.child = pexpect.spawn(program, timeout=1)
        self.atprompt = False
        self.prompt = prompt
        self.flush()

    def command(self, prompt, response):
        if prompt is None:
            if not self.showing(self.prompt):
                self.output(self.prompt)
            self.toprompt()
        else:
            self.child.expect(prompt)

        self.child.sendline(response)
        self.atprompt = False

    def showing(self, text):
        return self.getoutput()[-len(text):] == text

    def toprompt(self):
        if not self.atprompt:
            self.child.expect(self.prompt)
            self.atprompt = True

    def getoutput(self):
        return self.child.logfile_read.getvalue()

    def output(self, text):
        self.child.logfile_read.write(text)

    def flush(self):
        self.child.logfile_read = StringIO()

    def quit(self, cmd='quit'):
        self.toprompt()
        self.child.sendline(cmd)
        self.child.expect(pexpect.EOF)


def run_session(debug=False):
    command = """
    pyditz --no-search --no-pager --no-plugins
    -c ui.name=Dilbert
    -c ui.email=dilbert@cubicle.com
    -c highlight.enable=no
    -c vcs.enable=no
    """.strip().replace("\n", ' ')

    ditz = CmdSession(command, "Ditz: ")

    for line in fileinput.input():
        m = re.match(r'\.\. command: *(.*)', line)
        if m:
            cmd = m.group(1)
            ditz.command(None, cmd)
            continue

        m = re.match(r'\.\. prompt: *(.*)', line)
        if m:
            prompt = m.group(1) or None
            continue

        m = re.match(r'\.\. reply: *(.*)', line)
        if m:
            reply = m.group(1)
            ditz.command(prompt, reply)
            continue

        m = re.match(r'\.\. (literal)?include:: */(.+\.txt)', line)
        if m:
            recfile = m.group(2)

            ditz.toprompt()
            output = ditz.getoutput()
            lines = output.split("\r\n")[:-1]
            output = "\n".join(lines).rstrip() + "\n"
            ditz.flush()

            with open(recfile, "w") as fp:
                fp.write(output)

            if debug:
                print()
                print("===", recfile, "===")
                print()
                print(output)
            else:
                print("Wrote", recfile)

    ditz.quit()


if __name__ == "__main__":
    run_session()
