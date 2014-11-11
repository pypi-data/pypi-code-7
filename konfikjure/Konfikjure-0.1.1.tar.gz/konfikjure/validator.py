# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of Konfikjure.
# See the file 'docs/LICENSE.txt' for copying permission.

import os.path

from konfikjure.colors import purple, yellow


class Validator(object):
    options = None

    def __init__(self, default):
        self.default = str(default)

    def check(self, value):
        raise NotImplementedError

    def prompt(self, explanation, question):
        for line in explanation.split('\n'):
            print line.strip()

        if self.options:
            q = '%s (%s)?' % (purple(question), yellow(self.options))
        else:
            q = '%s?' % purple(question)

        value = raw_input('> %s [%s]: ' % (q, yellow(self.default)))
        print
        return self.check(value or self.default)


class ValidationError(Exception):
    pass


class ExistingFile(Validator):
    def check(self, value):
        if not value or not os.path.isfile(value):
            raise ValidationError('File not found')

        return value


class ExistingDirectory(Validator):
    def check(self, value):
        if not value or not os.path.isdir(value):
            raise ValidationError('Directory not found')

        return value


class Boolean(Validator):
    TRUE = 'y', 'yes', 'on', 'true'
    FALSE = 'n', 'no', 'off', 'false'
    options = 'y/n'

    def check(self, value):
        if value.lower() in self.TRUE:
            return 'true'

        if value.lower() in self.FALSE:
            return 'false'

        raise ValidationError('Unknown boolean value')


class Int(Validator):
    def check(self, value):
        if value.startswith('0x'):
            try:
                return int(value[2:], 16)
            except:
                raise ValidationError('Invalid hexadecimal integer')

        if not value.isdigit():
            raise ValidationError('Invalid integer')

        return int(value)


class Options(Validator):
    def __init__(self, explanation, question, default, *options):
        Validator.__init__(self, explanation, question, default)
        self.options = options

    def check(self, value):
        if value not in self.options:
            raise ValidationError('Invalid option')

        return value


class Text(Validator):
    def check(self, value):
        if not value:
            raise ValidationError('No text has been provided')

        return value
