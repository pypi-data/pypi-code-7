# Copyright 2014 Foursquare Labs Inc. All Rights Reserved.

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import os

from pants.backend.core.tasks.task import Task


class Tagger(Task):
  @classmethod
  def product_types(cls):
    return ['tagged_build_graph']

  def execute(self):
    basenames = self.context.config.getdict('target-tags', 'by-basename') or {}
    prefixes = self.context.config.getdict('target-tags', 'by-prefix') or {}
    if prefixes or basenames:
      for target in self.context.targets():
        this_basename = os.path.basename(target.address.spec_path)
        target._tags |= set(basenames.get(this_basename, []))
        for prefix in prefixes:
          if target.address.spec.startswith(prefix):
            target._tags |= set(prefixes[prefix])
