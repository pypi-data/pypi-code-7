#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import sys
import time

import pytest

sys.path.append('src/')
from timeout_wrapper import timeout, TimeoutException


# Variables ===================================================================
SLEEP_TIME = 5
WAIT_TIME = 1
MESSAGE = "Timeouted!"


# Functions & classes =========================================================
def test_wrapper():
    @timeout(WAIT_TIME, 1111)
    def sleep():
        time.sleep(SLEEP_TIME)

    ts = time.time()
    assert sleep() == 1111
    te = time.time()

    assert int(te - ts) == WAIT_TIME, "Timeout takes too long!"


def test_default_value():
    @timeout(WAIT_TIME, "timeouted")
    def sleep2():
        time.sleep(SLEEP_TIME)

    assert sleep2() == "timeouted"


def test_exception():
    @timeout(WAIT_TIME)
    def sleep3():
        time.sleep(SLEEP_TIME)

    with pytest.raises(TimeoutException) as excinfo:
        sleep3()


def test_exception_message():
    @timeout(WAIT_TIME, exception_message=MESSAGE)
    def sleep3():
        time.sleep(SLEEP_TIME)

    with pytest.raises(TimeoutException) as excinfo:
        sleep3()
        assert excinfo.message == MESSAGE
