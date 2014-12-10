from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

from collections import defaultdict
import os

from pants.base.build_environment import get_buildroot
from pants.base.build_file import BuildFile


class LazySourceMapper(object):
  """A utility for lazily mapping source files to the addresses of targets that own them

  LazySourceMapper memoizes its results, and populating the BuildGraph is expensive, so in general
  there should only be one instance of it.
  """

  def __init__(self, context):
    """Initialize LazySourceMapper

    :param Context context: A Context object as provided to Task instances.
    """
    self.build_file_parser = context.build_file_parser
    self.build_graph = context.build_graph
    self.address_mapper = context.address_mapper
    self.source_to_address = defaultdict(set)

  def _nearest_build_file_family(self, directory):
    """Walks up the directory tree until it finds a BUILD file.  Stops at the buildroot."""
    if directory.startswith(('.pants.d', '.buildgen', 'out')):
      raise Exception('Tried to find a BUILD file in a banned directory: {0}'
                      .format(directory))

    candidate_directory = directory
    while candidate_directory:
      candidate_build_file = BuildFile.from_cache(root_dir=get_buildroot(),
                                                  relpath=candidate_directory,
                                                  must_exist=False)
      if candidate_build_file.exists():
        return list(candidate_build_file.family())
      else:
        candidate_directory = os.path.dirname(candidate_directory)
    raise ValueError('No candidate BUILD file found for source in directory {directory}.'
                     .format(directory=directory))

  def _compute_source_addresses(self, source):
    """The actual work of populating the memoized mapping of source to owning addresses."""

    source_dir = os.path.dirname(source)
    candidate_build_file_family = self._nearest_build_file_family(source_dir)
    for build_file in candidate_build_file_family:
      address_map = self.address_mapper._address_map_from_spec_path(build_file.spec_path)
      for address, addressable in address_map.values():
        target = self.build_graph._target_addressable_to_target(address, addressable)
        if target.has_sources():
          for target_source in target.sources_relative_to_buildroot():
            self.source_to_address[target_source].add(target.address)
    if source not in self.source_to_address:
      raise ValueError('No owning target found for source {source}'.format(source=source))
    return self.source_to_address[source]

  def _target_addresses_from_source_iter(self, source):
    """A convenience iterator that uses the memoized results and filters target types.

    :param string source: The source to look up.
    :param tuple<type(Target instance)> allowed_target_types: The types of target instances that
      we're actually interested in considering as owners.
    """
    if source not in self.source_to_address:
      self._compute_source_addresses(source)
    addresses = self.source_to_address[source]
    return addresses

  def target_addresses_from_source(self, *args, **kwargs):
    """Wrapper around `target_addresses_from_source_iter` that normalizes the results to a set."""
    return set(self._target_addresses_from_source_iter(*args, **kwargs))
