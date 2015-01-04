# -*- coding: utf-8 -*-

# $Id$

import os
import subprocess


def run(command, reactor):
    proc = subprocess.Popen(
        command,
        shell=True,
        stdin=None,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    reactor.start()
    fd = proc.stdout.fileno()
    data = os.read(fd, 1)
    while data:
        reactor.feed(data)
        data = os.read(fd, 1)
    reactor.stop(proc.wait())


