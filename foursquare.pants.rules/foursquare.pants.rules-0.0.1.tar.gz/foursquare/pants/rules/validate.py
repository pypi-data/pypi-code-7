# Copyright 2014 Foursquare Labs Inc. All Rights Reserved.

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import os

from pants.backend.core.tasks.task import Task


class Validate(Task):
  def __init__(self, *args, **kwargs):
    super(Validate, self).__init__(*args, **kwargs)
    self._transitive_closure_cache = {}

  def prepare(self, round_manager):
    round_manager.require_data('tagged_build_graph')

  @classmethod
  def product_types(cls):
    return ['validated_build_graph']

  def execute(self):
    if 'buildgen' in self.context.requested_goals:
      return
    violations = []
    for target in self.context.targets():
      if 'exempt' not in target.tags:
        violations.extend(self.dependee_violations(target))
        violations.extend(self.banned_tag_violations(target))
        violations.extend(self.required_tag_violations(target))

    direct_violations = [v for v in violations if v.direct]

    if direct_violations:
      violations = direct_violations

    for v in violations:
      self.context.log.error(v.msg())

    assert(not violations)

  def extract_matching_tags(self, prefix, target):
    return set([tag.split(':', 1)[1] for tag in target.tags if tag.startswith(prefix)])

  def nonexempt_deps(self, address):
    if address not in self._transitive_closure_cache:
      computed_closure = self.context.build_graph.transitive_subgraph_of_addresses([address])
      self._transitive_closure_cache[address] = [
        dep for dep in computed_closure
        if dep.address != address and 'exempt' not in dep.tags
      ]
    return self._transitive_closure_cache[address]

  def dependee_violations(self, target):
    for dep in self.nonexempt_deps(target.address):
      for must_have in self.extract_matching_tags('dependees_must_have:', dep):
        if must_have not in target.tags:
          yield PrivacyViolation(target, dep, must_have)

  def banned_tag_violations(self, target):
    banned_tags = self.extract_matching_tags('dependencies_cannot_have:', target)
    if banned_tags:
      for dep in self.nonexempt_deps(target.address):
        for banned in banned_tags:
          if banned in dep.tags:
            yield BannedTag(target, dep, banned)

  def required_tag_violations(self, target):
    required_tags = self.extract_matching_tags('dependencies_must_have:', target)
    if required_tags:
      for dep in self.nonexempt_deps(target.address):
        for required in required_tags:
          if required not in dep.tags:
            yield MissingTag(target, dep, required)

class BuildGraphRuleViolation(object):
  def __init__(self, target, dep, tag):
    self.target = target
    self.dep = dep
    self.tag = tag
    self.direct = dep in target.dependencies


class BannedTag(BuildGraphRuleViolation):
  def msg(self):
    return '%s bans dependency on %s (via tag: %s)' % \
      (self.target.address.spec, self.dep.address.spec, self.tag)


class MissingTag(BuildGraphRuleViolation):
  def msg(self):
    return '%s requires dependencies to have tag %s and thus cannot depend on %s' \
        % (self.target.address.spec, self.tag, self.dep.address.spec)


class PrivacyViolation(BuildGraphRuleViolation):
  def msg(self):
    return '%s cannot depend on %s without having tag %s' \
        % (self.target.address.spec, self.dep.address.spec, self.tag)
