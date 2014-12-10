# Copyright 2013 Foursquare Labs Inc. All Rights Reserved.

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

from contextlib import contextmanager
import sys

from pants.backend.core.tasks.console_task import ConsoleTask
from pants.backend.core.tasks.task import Task

from foursquare.pants.changed.lazy_source_mapper import LazySourceMapper

# TODO(davidt): Move into git scm
def git_changed_paths(diffspec):
  import subprocess
  cmd = ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', diffspec]
  return [line.strip() for line in subprocess.check_output(cmd).split('\n')]


class NoopExecTask(Task):
  def execute(self):
    pass


class ChangedTask(Task):
  @classmethod
  def register_options(cls, register):
    super(ChangedTask, cls).register_options(register)
    register(
      '--diffspec', '--shas',
      default=None,
      action='store',
      help='scm diffspecs from which to extract changed files.'
    )

    register(
      '--changes-since',
      default='origin/master',
      action='store',
      help='scm spec relative to which "local" changes are determined.'
    )

    register(
      '--no-dependees', '--nd',
      default=False,
      action='store_true',
      help='Run on the changed targets, but not their dependees.'
    )

    register(
      '--direct-dependees', '--dd',
      default=None,
      action='store_true',
      help='Run on the changed targets and its dependees (default unless --nd or --td).'
    )

    register(
      '--transitive-dependees', '--td',
      default=False,
      action='store_true',
      help='Run on the changed targets and all of their transitive dependees.'
    )


  def prepare(self, round_manager):
    if self.goal_name() in self.context.requested_goals:
      # Need to opt out if we aren't the goal actually being run
      no_dependees = self.get_options().no_dependees
      direct_dependees = self.get_options().direct_dependees
      transitive_dependees = self.get_options().transitive_dependees
      if direct_dependees is None and not no_dependees and not transitive_dependees:
        direct_dependees = True
      count = sum(int(bool(option))
                  for option in [no_dependees, direct_dependees, transitive_dependees])
      if count > 1:
        raise

      changed_targets = list(self.target_roots_from_scm())
      build_graph = self.context.build_graph
      def populate_build_graph():
        for address in self.context.address_mapper.scan_addresses():
          build_graph.inject_address_closure(address)
      if no_dependees:
        target_roots = changed_targets[:]
      elif direct_dependees:
        target_roots = set(changed_targets)
        populate_build_graph()
        for target in changed_targets:
          target_roots.update(set(
            build_graph.get_target(dependee_address)
            for dependee_address in build_graph.dependents_of(target.address)
          ))
      elif transitive_dependees:
        target_roots = set(changed_targets)
        populate_build_graph()
        build_graph.walk_transitive_dependee_graph(
          [t.address for t in changed_targets],
          target_roots.add,
        )
      else:
        raise

      self.context.log.info('{} found {} targets on which to operate{}{}'.format(
        self.goal_name(),
        len(target_roots),
        ('.', ':\n')[bool(target_roots)],
        '\n'.join(['    * {}'.format(t.address.reference()) for t in sorted(target_roots)])
        )
      )
      self.context.replace_targets(list(target_roots))
      super(ChangedTask, self).prepare(round_manager)

  _source_mapper = None
  @property
  def source_mapper(self):
    """An instance of LazySourceMapper for mapping sources to their owning target addresses."""
    if self._source_mapper is None:
      self._source_mapper = LazySourceMapper(self.context)
      for target in self.context.build_graph.targets():
        for source in target.sources_relative_to_buildroot():
          self._source_mapper.source_to_address[source].add(target.address)
    return self._source_mapper

  def target_roots_from_scm(self):
    """Determines the changed targets using the SCM workspace."""
    if self.get_options().diffspec:
      changed_files = git_changed_paths(self.get_options().diffspec)
    else:
      changed_files = self.context.workspace.touched_files(parent=self.get_options().changes_since)
    for candidate_source in changed_files:
      try:
        addresses = self.source_mapper.target_addresses_from_source(candidate_source)
        for address in addresses:
          self.context.build_graph.inject_address_closure(address)
          yield self.context.build_graph.get_target(address)
      except ValueError as e:
        # No target owned this changed source.  That's okay.
        pass


class ListChanged(ChangedTask, ConsoleTask):
  @classmethod
  def goal_name(cls):
    return 'what-changed'

  def console_output(self, targets):
    return [t.address.reference() for t in self.context.target_roots]


class CompileChanged(ChangedTask, NoopExecTask):
  @classmethod
  def goal_name(cls):
    return 'compile-changed'

  def prepare(self, round_manager):
    super(CompileChanged, self).prepare(round_manager)
    round_manager.require_data('classes_by_target')
    round_manager.require_data('classes_by_source')


class TestChanged(ChangedTask, NoopExecTask):
  @classmethod
  def goal_name(cls):
    return 'test-changed'

  def prepare(self, round_manager):
    super(TestChanged, self).prepare(round_manager)
    round_manager.require_data('junit_tests_ran')


class ValidateChanged(ChangedTask, NoopExecTask):
  @classmethod
  def goal_name(cls):
    return 'validate-changed'

  def prepare(self, round_manager):
    super(ValidateChanged, self).prepare(round_manager)
    round_manager.require_data('validated_build_graph')
