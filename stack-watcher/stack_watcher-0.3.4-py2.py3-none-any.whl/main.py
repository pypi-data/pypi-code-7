"""Stackoverflow Watcher

A command line tool to notify you of new and relevant questions on Stack Overflow.

Usage:
  stack-watcher [--tag=<name>] [--interval=<seconds>] [--retriever=<import-path>]
                [--question=<import-path>]
  stack-watcher (-h | --help | --version)

Options:
  --version                  show program's version number and exit.
  -h, --help                 show this help message and exit.
  -t, --tag=<name>           a tag to constrain the question feed.
  -i, --interval=<seconds>   the interval between each feed request.
                             [default: 60]
  --retriever=<import-path>  the python import path to a retriever class.
                             [default: stack_watcher.Retriever]
  --question=<import-path>   the python import path to a question class.
                             [default: stack_watcher.Question]
"""
import os
import sys

from docopt import docopt

from stack_watcher import ClassLoader, __version__


def main():
    arguments = docopt(__doc__, version=__version__)

    # Add the current directory to the Python path, so subclasses can be found
    sys.path.append(os.getcwd())

    loader = ClassLoader()

    Retriever = loader.load_retriever_class(arguments['--retriever'])
    Question = loader.load_question_class(arguments['--question'])

    retriever = Retriever(
        tag=arguments['--tag'],
        interval=int(arguments['--interval']),
        question_cls=Question,
    )

    for question in retriever.questions():
        if question.adheres_to_rules:
            print(question)

if __name__ == '__main__':
    main()
