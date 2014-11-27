import unittest
import doublex

from inquirer.events import KeyEventGenerator, Event


class TestKeyEventGenerator(unittest.TestCase):
    def test_it_receives_events(self):
        event = object()
        with doublex.Mock() as generator:
            generator.key_gen().returns(event)

        sut = KeyEventGenerator(generator.key_gen)
        result = sut.next()

        self.assertEqual(event, result.value)
        doublex.assert_that(generator, doublex.verify())

    def test_it_returns_an_event(self):
        event = object()
        with doublex.Mock() as generator:
            generator.key_gen().returns(event)

        sut = KeyEventGenerator(generator.key_gen)
        result = sut.next()

        self.assertIsInstance(result, Event)
        doublex.assert_that(generator, doublex.verify())
