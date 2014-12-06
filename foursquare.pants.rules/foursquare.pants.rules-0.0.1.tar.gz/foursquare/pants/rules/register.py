# Copyright 2014 Foursquare Labs Inc. All Rights Reserved.

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

from pants.backend.core.tasks.task import Task
from pants.goal.task_registrar import TaskRegistrar as task

from foursquare.pants.rules.tag import Tagger
from foursquare.pants.rules.validate import Validate

class TriggerValidation(Task):
  """A noop task that depends on validation.

  This can be inserted into a goal to force validation to run before that goal.
  """
  def prepare(self, round_manager):
    round_manager.require_data('validated_build_graph')

  def execute(self):
    pass

def register():
  task(name='tag',action=Tagger).install().with_description('Add tags to targets.')

  task(name='validate',action=Validate).install().with_description('Validate BUILD dependencies.')

  task(name='require-validate',action=TriggerValidation).install('bootstrap',first=True)

