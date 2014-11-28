import unittest

from bubbler import Bubbler, Error

class BubblerTest(unittest.TestCase):
	def tearDown(self):
		Bubbler.contexts = {}

	def _testing_callable_1(self, event):
		return "Callable 1"

	def _testing_callable_2(self, event):
		return "Callable 2"

	def _testing_callable_3(self, event):
		return "Callable 3"

	def _testing_callable_args(self, event, *args, **kwargs):
		return {"args": args, "kwargs": kwargs}

	def _testing_callable_stop(self, event):
		event.stopped = True
		return "Callable Stop"

	def test_createDefaultContext(self):
		c = Bubbler.getContext()
		self.assertEquals('default', c.name)

	def test_createNamedContext(self):
		b = Bubbler('somename')
		c = Bubbler.getContext('somename')
		self.assertEquals(b, c)
		self.assertEquals('somename', c.name)

	def test_createExistingDefaultContext(self):
		b = Bubbler()
		self.assertRaises(Error, Bubbler)

	def test_createExistingNamedContext(self):
		b = Bubbler('somename')
		self.assertRaises(Error, Bubbler, 'somename')

	def test_bind(self):
		b = Bubbler()
		b.bind('event', self._testing_callable_1)
		self.assertEquals([self._testing_callable_1], b.handlers['event'])

	def test_bindMultiple(self):
		b = Bubbler()
		b.bind('event', self._testing_callable_1)
		b.bind('event', self._testing_callable_2)
		self.assertEquals([self._testing_callable_1, self._testing_callable_2], b.handlers['event'])

	def test_bindFirst(self):
		b = Bubbler()
		b.bind('event', self._testing_callable_1)
		b.bind('event', self._testing_callable_2, True)
		self.assertEquals([self._testing_callable_2, self._testing_callable_1], b.handlers['event'])

	def test_unbindAll(self):
		b = Bubbler()
		b.bind('event', self._testing_callable_1)
		b.bind('event', self._testing_callable_2)
		b.bind('event', self._testing_callable_3)
		b.bind('event/thing', self._testing_callable_1)
		b.bind('event/thing', self._testing_callable_2)
		b.bind('event/thing', self._testing_callable_3)
		b.unbind(self._testing_callable_2)
		self.assertEquals([self._testing_callable_1, self._testing_callable_3], b.handlers['event'])
		self.assertEquals([self._testing_callable_1, self._testing_callable_3], b.handlers['event/thing'])

	def test_unbindAll(self):
		b = Bubbler()
		b.bind('event', self._testing_callable_1)
		b.bind('event', self._testing_callable_2)
		b.bind('event', self._testing_callable_3)
		b.bind('event/thing', self._testing_callable_1)
		b.bind('event/thing', self._testing_callable_2)
		b.bind('event/thing', self._testing_callable_3)
		b.unbind(self._testing_callable_2, 'event/thing')
		self.assertEquals([self._testing_callable_1, self._testing_callable_2, self._testing_callable_3], b.handlers['event'])
		self.assertEquals([self._testing_callable_1, self._testing_callable_3], b.handlers['event/thing'])

	def test_trigger(self):
		b = Bubbler()
		b.bind('event', self._testing_callable_1)
		b.bind('event', self._testing_callable_2)
		b.bind('event', self._testing_callable_3)
		b.bind('event/thing', self._testing_callable_1)
		b.bind('event/thing', self._testing_callable_2, True)
		b.bind('event/thing', self._testing_callable_3)

		e = b.trigger('event/thing')
		self.assertEquals('event/thing', e.name)
		self.assertEquals(b, e.context)
		self.assertEquals([
			self._testing_callable_2,
			self._testing_callable_1,
			self._testing_callable_3,
			], e.handlers)
		self.assertEquals([
			self._testing_callable_2,
			self._testing_callable_1,
			self._testing_callable_3,
			self._testing_callable_1,
			self._testing_callable_2,
			self._testing_callable_3,
			], e.all_handlers)
		self.assertEquals(3, e.executed)
		self.assertEquals(6, e.all_executed)
		self.assertEquals(["Callable 2", "Callable 1", "Callable 3"], e.result)
		self.assertEquals([
			"Callable 2",
			"Callable 1",
			"Callable 3",
			"Callable 1",
			"Callable 2",
			"Callable 3",
			], e.all_result)
		self.assertEquals(False, e.stopped)

	def test_triggerWithArgs(self):
		b = Bubbler()
		b.bind('event', self._testing_callable_args)

		e = b.trigger('event', "foo", "bar", baz = "quux")
		self.assertEquals('event', e.name)
		self.assertEquals(b, e.context)
		self.assertEquals([self._testing_callable_args], e.handlers)
		self.assertEquals([self._testing_callable_args], e.all_handlers)
		self.assertEquals(1, e.executed)
		self.assertEquals(1, e.all_executed)
		self.assertEquals([{"args": ("foo", "bar"), "kwargs": {"baz": "quux"}}], e.result)
		self.assertEquals([{"args": ("foo", "bar"), "kwargs": {"baz": "quux"}}], e.all_result)
		self.assertEquals(False, e.stopped)

	def test_triggerStopped(self):
		b = Bubbler()
		b.bind('event', self._testing_callable_1)
		b.bind('event', self._testing_callable_stop)
		b.bind('event', self._testing_callable_2)

		e = b.trigger('event')
		self.assertEquals('event', e.name)
		self.assertEquals(b, e.context)
		self.assertEquals([self._testing_callable_1, self._testing_callable_stop, self._testing_callable_2], e.handlers)
		self.assertEquals([self._testing_callable_1, self._testing_callable_stop, self._testing_callable_2], e.all_handlers)
		self.assertEquals(2, e.executed)
		self.assertEquals(2, e.all_executed)
		self.assertEquals(["Callable 1", "Callable Stop"], e.result)
		self.assertEquals(["Callable 1", "Callable Stop"], e.all_result)
		self.assertEquals(True, e.stopped)
