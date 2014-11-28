class Error(Exception):
	"""A base error class for use by the Bubbler event system.

	This class serves only to differentiate Bubbler errors from other exceptions
	that might be thrown.
	"""
	pass

class Event(object):
	"""Represents a single event execution.

	The Event object contains important information about the event that has been
	executed.

	Attributes:
		name (string):
			The full name name of the event that was executed
		context (bubbler.Bubbler):
			The instance of the Bubbler context that holds the event handlers
			used in this instance
		handlers (list(callable)):
			All handlers registered for the event exactly matching name
		all_handlers (list(callable)):
			All handlers registered for any event matching name
		executed (int):
			The number of handlers exactly matching name that were executed
		all_executed (int):
			The total number of handlers that were executed
		result (list):
			The return values from each handler in the handlers list that was executed
		all_result (list)
			The return values from every handler that was executed
		stopped (boolean):
			Whether the execution of handlers was stopped.  Handlers may also set
			this to True in order to stop execution of later handlers.
	"""

	def __init__(self, name, context):
		"""Create a new Event instance.

		Params:
			name (string):
				Full event name
			context (bubbler.Bubbler):
				Bubbler context
		"""
		self.name = name
		self.context = context
		self.handlers = []
		self.all_handlers = []
		self.executed = 0
		self.all_executed = 0
		self.result = []
		self.all_result = []
		self.stopped = False

	def trigger(self, *args, **kwargs):
		"""Trigger this event.

		Any passed in args/kwargs are passed to the event handlers - if the event
		handlers cannot accept those arguments then they will cause an exception!
		"""
		current = self.name.split('/')
		while current:
			name = '/'.join(current)
			current.pop()
			if name in self.context.handlers:
				self.all_handlers += [(name, h) for h in self.context.handlers[name]] 
				if name == self.name:
					self.handlers += self.context.handlers[name]

		for name, handler in self.all_handlers:
			res = handler(self, *args, **kwargs)
			self.all_executed += 1
			self.all_result.append(res)
			if name == self.name:
				self.executed += 1
				self.result.append(res)
			if self.stopped:
				break

		self.all_handlers = [h for name, h in self.all_handlers]

class Bubbler(object):
	"""Represents a Bubbler context.

	Class Attributes:
		contexts (dict(bubbler.Bubbler)):
			All named Bubbler instances

	Attributes:
		name (string):
			Context name, used to retrieve the same context object across modules
		handlers (dict(list(callable))):
			All event handlers registered on this context
	"""

	contexts = {}

	def __init__(self, context_name = 'default'):
		"""Create a new Bubbler context

		Params:
			context_name (string):
				Name of this context

		Raises:
			bubbler.Error:
				If this context name already exists
		"""
		if context_name in self.contexts:
			raise Error("A context named '%s' already exists" % (context_name,))

		self.name = context_name
		self.handlers = {}

		self.contexts[self.name] = self

	@classmethod
	def getContext(self, context_name = 'default'):
		"""Get a context by name, create the default context if it does not exist

		Params:
			context_name (string):
				Context name

		Raises:
			KeyError:
				If the context name does not exist

		Returns:
			bubbler.Bubbler:
				Named context
		"""
		if context_name == 'default' and 'default' not in self.contexts:
			self('default')

		return self.contexts[context_name]

	def bind(self, event_name, callback, first = False):
		"""Bind a callback to an event

		Params:
			event_name (string):
				Name of the event to bind to
			callback (callable):
				Callback that will be called when the event is triggered
			first (boolean):
				If True, this callback is placed before all the other events already
				registered for this event, otherwise it is placed at the end.
		"""
		if event_name not in self.handlers:
			self.handlers[event_name] = []

		if first:
			self.handlers[event_name].insert(0, callback)
		else:
			self.handlers[event_name].append(callback)

	def unbind(self, callback, event_name = None):
		"""Unbind a callback from an event

		Params:
			callback (callable):
				Callback to unbind
			event_name (string):
				If None (default) this callback is removed from every event to
				which it's bound.  If a name is given then it is only removed from
				that event, if it is bound to that event.
		"""
		if event_name is None:
			for name in self.handlers.keys():
				self.unbind(callback, name)
			return

		if callback in self.handlers[event_name]:
			self.handlers[event_name].remove(callback)

	def trigger(self, event_name, *args, **kwargs):
		"""Trigger an event on this context.

		Params:
			event_name (string):
				Event name to trigger

		Args and kwargs are passed to each handler - see the bubbler.Event class
		for more information.

		Returns:
			bubbler.Event:
				Event instance after execution of all handlers
		"""
		ev = Event(event_name, self)
		ev.trigger(*args, **kwargs)
		return ev
