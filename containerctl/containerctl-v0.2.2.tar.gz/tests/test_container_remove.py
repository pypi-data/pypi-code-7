"""Test container removal."""
from .base import TestSimpleContainer
from containerctl import Container, ContainerError


class TestContainerRemove(TestSimpleContainer):
    """Container.remove"""
    def remove(self, path, latest=None):
        rmi_args = ['docker', 'rmi']
        rmi_kwargs = {'cwd': path}

        tags = self.get_tags(self.versions, latest)
        want_results = [(tag, True) for tag in tags]

        container = Container.from_path(path)
        for n in xrange(len(tags)):
            container._docker._mock.add_return(0)
        results = container.remove(latest)
        self.assertEqual(want_results, results)

        for tag in tags:
            call = container._docker._mock.next_call()
            self.assertEqual(rmi_args + [tag], list(call[4]['args']))
            self.assertEqual(rmi_kwargs, dict(call[4]['kwargs']))

    def test_defaults(self):
        path = self.create_container(self.name)
        self.remove(path)

    def test_latest(self):
        path = self.create_container(self.name)
        self.remove(path, True)

    def test_docker_failure(self):
        tags = self.get_tags(self.versions, True)
        want_results = [(tags[0], False)] + [(tag, True) for tag in tags[1:]]

        path = self.create_container(self.name)
        container = Container.from_path(path)
        container._docker._mock.add_return(1)
        for n in xrange(len(tags) - 1):
            container._docker._mock.add_return(0)
        results = container.remove(True)
        self.assertEqual(want_results, results)

    def test_docker_missing(self):
        path = self.create_container(self.name)
        container = Container.from_path(path)
        container._docker._mock.add_return(OSError('test docker missing'))
        self.assertRaises(ContainerError, container.remove)
