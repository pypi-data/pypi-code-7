# Copyright 2014 Foursquare Labs Inc. All Rights Reserved.

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

from pants.goal.task_registrar import TaskRegistrar

from foursquare.pants.changed.tasks import CompileChanged, ListChanged, TestChanged, ValidateChanged


def register():
  tasks = [
    (ListChanged, 'List'),
    (ValidateChanged, 'Validate'),
    (CompileChanged, 'Compile'),
    (TestChanged, 'Test'),
  ]

  for task, verb in tasks:
    desc = '{} targets containing local changes (or changes in diffspec)'.format(verb)
    TaskRegistrar(name=task.goal_name(), action=task).install().with_description(desc)
