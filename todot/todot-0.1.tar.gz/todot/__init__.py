#!/bin/env python

import argparse
import re
import string

INFILE_HELP = "the input todo file"

parser = argparse.ArgumentParser('todot')
parser.add_argument('INFILE', help=INFILE_HELP)
args = parser.parse_args()

def fail(message, suggestion=None):
    print("Error:", message)
    if suggestion: print("Note:", suggestion)
    exit(1)

name = "[\w-]+"
task_re = re.compile(r"(%s)\s*=\s*(.*?)\s*\[(%s)\]$" % (name, name))
dpnd_re = re.compile(r"(%s)\s*>\s*(%s)$" % (name, name))

class ParseException(RuntimeError): pass

class Task:
    def __init__(self, name, desc, status):
        self.name = name
        self.desc = desc
        self.status = status
        self.children = set()
        self.parents = set()
    def __repr__(self):
        return "%s:%s" % (self.name, self.status)
    def dot_name(self):
        return string.replace(self.name, "-", "_")
    def dot_desc(self):
        return '"%s"' % string.replace(self.desc, '"', '\\"')

def parse_file(file_name):
    tasks = {}
    dependencies = set()

    line_number = 0
    for line in open(file_name):
        line_number += 1
        comment = line.find("#")
        if comment > 0: line = line[:comment]
        line = line.strip()

        task = task_re.match(line)
        dpnd = dpnd_re.match(line)
        if line == "":
            continue
        elif task:
            name = task.group(1)
            desc = task.group(2)
            status = task.group(3)
            tasks[name] = Task(name, desc, status)
        elif dpnd:
            parent = dpnd.group(1)
            child = dpnd.group(2)
            dependencies.add((parent,child))
        else:
            raise ParseException("Syntax error: %s:%d" % (file_name, line_number))

    for d in dependencies:
        if not tasks.has_key(d[0]): raise ParseException("Task '%s' was never defined." % d[0])
        if not tasks.has_key(d[1]): raise ParseException("Task '%s' was never defined." % d[1])
        tasks[d[0]].children.add(tasks[d[1]])
        tasks[d[1]].parents.add(tasks[d[0]])

    return tasks

def print_dot_file(tasks):
    print "digraph G {"
    for t in tasks.values():
        print "    %s [label=%s]" % (t.dot_name(), t.dot_desc())
    print
    for t in tasks.values():
        for d in t.children:
            print "    %s -> %s" % (t.dot_name(), d.dot_name())
    print "}"

def main():
    print_dot_file(parse_file(args.INFILE))

if __name__ == "__main__": main()