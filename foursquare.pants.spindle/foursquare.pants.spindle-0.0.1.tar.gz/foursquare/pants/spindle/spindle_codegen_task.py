# Copyright 2013 Foursquare Labs Inc. All Rights Reserved.

from collections import defaultdict
import glob
from itertools import chain
import os
import re

from twitter.common import log
from twitter.common.dirutil import safe_mkdir

from pants.backend.jvm.targets.exportable_jvm_library import ExportableJvmLibrary
from pants.backend.jvm.targets.java_library import JavaLibrary
from pants.backend.jvm.targets.scala_library import ScalaLibrary
from pants.backend.jvm.tasks.nailgun_task import NailgunTask
from pants.base.address import SyntheticAddress
from pants.base.build_environment import get_buildroot
from pants.base.build_file_aliases import BuildFileAliases
from pants.base.exceptions import TaskError
from pants.goal.task_registrar import TaskRegistrar as task


class SpindleGen(NailgunTask):
  @classmethod
  def get_fingerprint_strategy(cls):
    return None

  def __init__(self, context, workdir):
    NailgunTask.__init__(self, context, workdir)

    self.args = context.config.getlist('spindle-gen', 'args', [])
    self.jvm_options = context.config.getlist('spindle-gen', 'jvm_options', [])
    self.main_class = context.config.get(
      'spindle-gen',
      'main_class',
      default='com.foursquare.spindle.codegen.binary.ThriftCodegen',
    )

    self._spindle_bootstrap_key = 'spindle'
    bootstrap_tools = context.config.getlist('spindle-gen', 'bootstrap-tools')
    self._jvm_tool_bootstrapper.register_jvm_tool(self._spindle_bootstrap_key, bootstrap_tools)

    self.scalate_workdir = os.path.join(workdir, 'scalate_workdir')
    self.namespace_out = os.path.join(workdir, 'scala_record')

    self.setup_artifact_cache_from_config(config_section='spindle-gen')
    self.template = context.config.getdict('spindle-gen', 'scala_record', {}).get('template')
    self.javaTemplate = context.config.getdict('spindle-gen', 'scala_record', {}).get('javaTemplate')

  @classmethod
  def product_types(cls):
    return [
      'scala',
    ]

  @property
  def config_section(self):
    return 'spindle-gen'

  @property
  def spindle_classpath(self):
    return self._jvm_tool_bootstrapper.get_jvm_tool_classpath(self._spindle_bootstrap_key)

  @property
  def synthetic_target_extra_dependencies(self):
    dep_specs = self.context.config.getdict('spindle-gen', 'scala_record', {}).get('deps')
    return set(chain.from_iterable(self.context.resolve(spec) for spec in dep_specs))

  def codegen_targets(self):
    return self.context.targets(lambda t: isinstance(t, ScalaRecordLibrary))

  def sources_generated_by_target(self, target):
    relative_sources = []
    for thrift_source in target.sources_relative_to_buildroot():
      relative_sources.extend(calculate_genfiles(thrift_source))
    return [os.path.join(self.namespace_out, rel_source) for rel_source in relative_sources]

  def execute_codegen(self, targets):
    bases, sources = self._calculate_sources(targets, lambda t: isinstance(t, ScalaRecordLibrary))
    safe_mkdir(self.namespace_out)
    safe_mkdir(self.scalate_workdir)

    classpath = self.spindle_classpath
    args = [
      '--template', self.template,
      '--java_template', self.javaTemplate,
      '--thrift_include', ':'.join(bases),
      '--namespace_out', self.namespace_out,
      '--working_dir', self.scalate_workdir,
    ]
    args.extend(self.args)
    args.extend(sources)

    log.debug('Executing: %s %s' % (self.main_class, ' '.join(args)))
    result = self.runjava(classpath=classpath,
                          main=self.main_class,
                          jvm_options=self.jvm_options,
                          args=args,
                          workunit_name='generate')
    if result != 0:
      raise TaskError('%s returned %d' % (self.main_class, result))

  def execute(self):
    targets = self.codegen_targets()
    with self.invalidated(targets,
                          invalidate_dependents=True,
                          fingerprint_strategy=self.get_fingerprint_strategy()) as invalidation_check:
      for vts in invalidation_check.invalid_vts_partitioned:
        invalid_targets = vts.targets
        self.execute_codegen(invalid_targets)

      invalid_vts_by_target = dict([(vt.target, vt) for vt in invalidation_check.invalid_vts])
      vts_artifactfiles_pairs = defaultdict(list)

      for target in targets:
        java_synthetic_name = '{0}-{1}'.format(target.id, 'java')
        java_sources_rel_path = os.path.relpath(self.namespace_out, get_buildroot())
        java_spec_path = java_sources_rel_path
        java_synthetic_address = SyntheticAddress(java_spec_path, java_synthetic_name)
        java_generated_sources = [os.path.join(os.path.dirname(source), 'java_{0}.java'.format(os.path.basename(source))) for source in self.sources_generated_by_target(target)]
        java_relative_generated_sources = [os.path.relpath(src, self.namespace_out)
                                           for src in java_generated_sources]
        java_synthetic_target = self.context.add_new_target(
          address=java_synthetic_address,
          target_type=JavaLibrary,
          dependencies=self.synthetic_target_extra_dependencies,
          sources_rel_path=java_sources_rel_path,
          sources=java_relative_generated_sources,
          derived_from=target,
        )

        build_graph = self.context.build_graph

        # NOTE(pl): This bypasses the convenience function (Target.inject_dependency) in order
        # to improve performance.  Note that we can walk the transitive dependee subgraph once
        # for transitive invalidation rather than walking a smaller subgraph for every single
        # dependency injected.  This walk is done below, after the scala synthetic target is
        # injected.
        for concrete_dependency_address in build_graph.dependencies_of(target.address):
          build_graph.inject_dependency(
            dependent=java_synthetic_target.address,
            dependency=concrete_dependency_address,
          )

        if target in invalid_vts_by_target:
          vts_artifactfiles_pairs[invalid_vts_by_target[target]].extend(java_generated_sources)

        synthetic_name = '{0}-{1}'.format(target.id, 'scala')
        sources_rel_path = os.path.relpath(self.namespace_out, get_buildroot())
        spec_path = sources_rel_path
        synthetic_address = SyntheticAddress(spec_path, synthetic_name)
        generated_sources = ['{0}.{1}'.format(source, 'scala') for source in self.sources_generated_by_target(target)]
        relative_generated_sources = [os.path.relpath(src, self.namespace_out)
                                      for src in generated_sources]
        synthetic_target = self.context.add_new_target(
          address=synthetic_address,
          target_type=ScalaLibrary,
          dependencies=self.synthetic_target_extra_dependencies,
          sources_rel_path=sources_rel_path,
          sources=relative_generated_sources,
          derived_from=target,
          java_sources=[java_synthetic_target.address.spec],
        )

        # NOTE(pl): This bypasses the convenience function (Target.inject_dependency) in order
        # to improve performance.  Note that we can walk the transitive dependee subgraph once
        # for transitive invalidation rather than walking a smaller subgraph for every single
        # dependency injected.  This walk also covers the invalidation for the java synthetic
        # target above.
        for dependent_address in build_graph.dependents_of(target.address):
          build_graph.inject_dependency(dependent=dependent_address,
                                        dependency=synthetic_target.address)
        # NOTE(pl): See the above comment.  The same note applies.
        for concrete_dependency_address in build_graph.dependencies_of(target.address):
          build_graph.inject_dependency(
            dependent=synthetic_target.address,
            dependency=concrete_dependency_address,
          )
        build_graph.walk_transitive_dependee_graph(
          [target.address],
          work=lambda t: t.mark_transitive_invalidation_hash_dirty(),
        )

        if target in self.context.target_roots:
          self.context.target_roots.append(synthetic_target)
        if target in invalid_vts_by_target:
          vts_artifactfiles_pairs[invalid_vts_by_target[target]].extend(generated_sources)

      if self.artifact_cache_writes_enabled():
        self.update_artifact_cache(vts_artifactfiles_pairs.items())

  def _calculate_sources(self, thrift_targets, target_filter):
    bases = set()
    sources = set()
    def collect_sources(target):
      if target_filter(target):
        bases.add(target.target_base)
        sources.update(target.sources_relative_to_buildroot())

    for target in thrift_targets:
      target.walk(collect_sources)
    return bases, sources


# Slightly hacky way to figure out which files get generated from a particular thrift source.
# TODO(benjy): This could be emitted by the codegen tool. That would also allow us to easily support 1:many codegen.
NAMESPACE_PARSER = re.compile(r'^\s*namespace\s+([^\s]+)\s+([^\s]+)\s*$')

def calculate_genfiles(source):
  with open(source, 'r') as thrift:
    lines = thrift.readlines()
  namespaces = {}
  for line in lines:
    match = NAMESPACE_PARSER.match(line)
    if match:
      lang = match.group(1)
      namespace = match.group(2)
      namespaces[lang] = namespace

  genfiles = defaultdict(set)
  namespace = namespaces.get('java')

  if not namespace:
    raise TaskError('No namespace provided in source: %s' % source)

  return calculate_scala_record_genfiles(namespace, source)

def calculate_scala_record_genfiles(namespace, source):
  """Returns the generated file basenames, add .java or .scala to get the full path."""
  basepath = namespace.replace('.', '/')
  name = os.path.splitext(os.path.basename(source))[0]
  return [os.path.join(basepath, name)]

# so these 'Library' classes are what you are in fact instantiating in a build file.
# Mappings are stored in foursquare.web/src/python/foursquare/pants/__init__.py
# eg scala_record_library -> ScalaRecordLibrary
# Note: our naming is slightly confusing. A ScalaRecordLibrary target is actually a thrift target
# and is used in src/thrift. A ScalaLibrary target is used for src/jvm build files.
class ScalaRecordLibrary(ExportableJvmLibrary):
  """Defines a target that builds scala_record stubs from a thrift IDL file."""

  def __init__(self, *args, **kwargs):
    super(ScalaRecordLibrary, self).__init__(*args, **kwargs)
    self.add_labels('scala', 'codegen', 'synthetic')

  def _as_jar_dependency(self):
    return ExportableJvmLibrary._as_jar_dependency(self).withSources()


def register():
  task(name='custom-thrift', action=SpindleGen, dependencies=['bootstrap']).install('gen')

def dependencies():
  return ['foursquare.pants.rules']

def aliases():
  return BuildFileAliases.create(targets={'scala_record_library': ScalaRecordLibrary,})
