"""Test container push."""
from .base import TestSimpleContainer
from containerctl import Container, ContainerError
from .mocks import patch_container, unpatch


class TestContainerPush(TestSimpleContainer):
    """Container.push"""
    def push(self, path, latest=None):
        inspect_args = ['docker', 'inspect']
        inspect_kwargs = {'cwd': path}
        push_args = ['docker', 'push']
        push_kwargs = inspect_kwargs

        container = Container.from_path(path)
        for n in xrange(len(self.versions) * 2 + 1):
            container._docker._mock.add_return(0)

        container.push(latest=latest)

        for tag in self.get_tags(self.versions):
            call = container._docker._mock.next_call()
            self.assertEqual(inspect_args + [tag], list(call[4]['args']))
            self.assertEqual(inspect_kwargs, dict(call[4]['kwargs']))

        for tag in self.get_tags(self.versions, latest):
            call = container._docker._mock.next_call()
            self.assertEqual(push_args + [tag], list(call[4]['args']))
            self.assertEqual(push_kwargs, dict(call[4]['kwargs']))

    def test_defaults(self):
        path = self.create_container(self.name)
        self.push(path)

    def test_latest(self):
        path = self.create_container(self.name)
        self.push(path, True)

    def test_not_built(self):
        path = self.create_container(self.name)
        container = Container.from_path(path)
        container._docker._mock.add_return(1)
        self.assertRaises(ContainerError, container.push)

    def test_docker_fail(self):
        path = self.create_container(self.name)
        container = Container.from_path(path)
        for version in self.versions:
            container._docker._mock.add_return(0)
        container._docker._mock.add_return(1)
        self.assertRaises(ContainerError, container.push)

    def test_docker_missing(self):
        path = self.create_container(self.name)
        container = Container.from_path(path)
        for version in self.versions:
            container._docker._mock.add_return(0)
        container._docker._mock.add_return(OSError('test docker missing'))
        self.assertRaises(ContainerError, container.push)

    def test_no_tags(self):
        unpatch()
        patch_container(None, [])
        try:
            path = self.create_container(self.name)
            container = Container.from_path(path)
            self.assertRaises(ContainerError, container.push)
        finally:
            unpatch()
            patch_container(self.version, self.versions)

