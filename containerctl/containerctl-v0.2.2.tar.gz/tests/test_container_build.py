"""Test container build."""
from .base import TestSimpleContainer
from containerctl import Container, ContainerError
from .mocks import patch_container, unpatch


class TestContainerBuild(TestSimpleContainer):
    """Container.build"""
    def build(self, path, remove=None, prebuild=None, nocache=None, latest=None):
        if remove is None:
            remove = True

        tags = self.get_tags(self.versions, latest)
        image = tags.pop()

        build_args = ['docker', 'build']
        if remove:
            build_args += ['--rm', '--force-rm']
        if nocache:
            build_args += ['--no-cache']
        build_args += ['-t', image, '.']
        build_kwargs = {'cwd': path}

        container = Container.from_path(path)
        if not remove:
            container.allow_remove = False
        container._docker._mock.add_return(0)
        for tag in tags:
            container._docker._mock.add_return(0)

        container.build(
            prebuild=prebuild,
            nocache=nocache,
            latest=latest,
        )

        call = container._docker._mock.next_call()
        self.assertEqual(build_args, list(call[4]['args']))
        self.assertEqual(build_kwargs, dict(call[4]['kwargs']))

        tag_kwargs = {'cwd': path}
        for tag in tags:
            tag_args = ['docker', 'tag', image, tag]
            call = container._docker._mock.next_call()
            self.assertEqual(tag_args, list(call[4]['args']))
            self.assertEqual(tag_kwargs, dict(call[4]['kwargs']))

    def test_defaults(self):
        path = self.create_container(self.name)
        self.build(path)

    def test_noremove(self):
        path = self.create_container(self.name)
        self.build(path, remove=False)

    def test_docker_build_fail(self):
        path = self.create_container(self.name)
        container = Container.from_path(path)
        container._docker._mock.add_return(1)
        self.assertRaises(ContainerError, container.build)

    def test_docker_tag_fail(self):
        path = self.create_container(self.name)
        container = Container.from_path(path)
        container._docker._mock.add_return(0)
        container._docker._mock.add_return(1)
        self.assertRaises(ContainerError, container.build, latest=True)

    def test_docker_missing(self):
        path = self.create_container(self.name)
        container = Container.from_path(path)
        container._docker._mock.add_return(OSError('test missing docker'))
        self.assertRaises(ContainerError, container.build)

    def test_dockerfile_missing(self):
        path = self.create_container(self.name, dockerfile=False)
        container = Container.from_path(path)
        self.assertRaises(ContainerError, container.build)

    def test_prebuild(self, filename=None):
        config = {}
        if filename:
            config['prebuild'] = './' + filename
        path = self.create_container(self.name, config)
        self.create_prebuild(path, filename)
        try:
            self.build(path)
            self.assertTrue(self.check_prebuild(path))
        finally:
            self.remove_prebuild(path, filename)

    def test_prebuild_disable(self):
        path = self.create_container(self.name)
        self.create_prebuild(path)
        try:
            self.build(path, prebuild=False)
            self.assertFalse(self.check_prebuild(path))
        finally:
            self.remove_prebuild(path)

    def test_prebuild_alternative(self):
        self.test_prebuild('other')

    def test_prebuild_fail(self):
        path = self.create_container(self.name)
        self.create_prebuild(path, fail=True)
        try:
            container = Container.from_path(path)
            self.assertRaises(ContainerError, container.build)
        finally:
            self.remove_prebuild(path)

    def test_nocache(self):
        path = self.create_container(self.name)
        self.build(path, nocache=True)

    def test_latest(self):
        path = self.create_container(self.name)
        self.build(path, latest=True)

    def test_verify_success(self):
        path = self.create_container(self.name)
        container = Container.from_path(path, True)
        for n in xrange(2):
            container._docker._mock.add_return(0)
        container.build()

    def test_verify_failure(self):
        unpatch()
        patch_container(self.unverified_versions[0], self.unverified_versions)
        try:
            path = self.create_container(self.name)
            container = Container.from_path(path, True)
            for n in xrange(2):
                container._docker._mock.add_return(0)
            self.assertRaises(ContainerError, container.build)
        finally:
            unpatch()
            patch_container(self.version, self.versions)

    def test_no_tags(self):
        unpatch()
        patch_container(None, [])
        try:
            path = self.create_container(self.name)
            container = Container.from_path(path)
            self.assertRaises(ContainerError, container.build)
        finally:
            unpatch()
            patch_container(self.version, self.versions)

    def is_built(self, built):
        path = self.create_container(self.name)
        inspect_args = ['docker', 'inspect', self.get_tag(self.version)]
        inspect_kwargs = {'cwd': path}

        container = Container.from_path(path)
        for tag in self.get_tags(self.versions):
            container._docker._mock.add_return(0 if built else 1)
        self.assertEqual(built, container.is_built())

        call = container._docker._mock.next_call()
        self.assertEqual(inspect_args, list(call[4]['args']))
        self.assertEqual(inspect_kwargs, dict(call[4]['kwargs']))

    def test_is_built_true(self):
        self.is_built(True)

    def test_is_built_false(self):
        self.is_built(False)

    def test_is_built_docker_missing(self):
        path = self.create_container(self.name)
        container = Container.from_path(path)
        container._docker._mock.add_return(OSError('test missing docker'))
        self.assertRaises(ContainerError, container.is_built)
