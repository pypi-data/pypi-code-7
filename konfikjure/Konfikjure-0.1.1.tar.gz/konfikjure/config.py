# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of Konfikjure.
# See the file 'docs/LICENSE.txt' for copying permission.

CONFIGFILES = []
VARIABLES = []


class Variable(object):
    def __init__(self, key, explanation, question, validator):
        self.key = key
        self.explanation = explanation
        self.question = question
        self.validator = validator

        VARIABLES.append(self)

    def prompt(self):
        return self.validator.prompt(self.explanation, self.question)


class Config(object):
    def __init__(self, filepath, layout):
        self.filepath = filepath
        self.layout = layout.strip()

        CONFIGFILES.append(self)

    def write(self, **kwargs):
        with open(self.filepath, 'wb') as f:
            f.write(self.layout % kwargs)
