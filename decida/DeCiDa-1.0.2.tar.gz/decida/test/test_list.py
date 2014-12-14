#!/usr/bin/env python
import sys, os, decida.test

def test_list() :
    files = os.listdir(decida.test.test_dir())
    non_tests = ("__init__", "test_list", "test_dir", "test_all")
    test_list = []
    for file in files :
        tail = os.path.basename(file)
        root, ext = os.path.splitext(tail)
        if ext == ".py" and not root in non_tests :
            test_list.append(root)
    return test_list
