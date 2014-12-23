import time
import threading
import pdb
import Adafruit_CharLCD as AdafruitLCD

class Node(object):
	def __init__(self, label='', nodes=None, controller_fn=None, *controller_argvs):

		self.label = label
		self.parent = None
		
		if nodes is None:
			nodes = []

		self.nodes = nodes

		for node in self.nodes:
			node._set_parent(self)

		self.controller_fn = controller_fn
		self.controller_argvs = controller_argvs

	def add_node(self, node):
		self.nodes.append(node)
		node._set_parent(self)

		return self

	def _set_parent(self, node):
		self.parent = node

		return self

	def controller(self, app):
		if callable(self.controller_fn):
			return self.controller_fn(app, self, *self.controller_argvs)

		return True

class App(object):
	def __init__(self, input_adapter, nodes, display_adapter):

		if nodes is None:
			nodes = []

		self._input_adapter = input_adapter
		self.display_adapter = display_adapter

		self._root_node = Node(nodes=nodes)
		self._highlighted_node = self._root_node.nodes[0]
		self._highlighted_index = 0;
		self._context_node = self._root_node
		self._loop = True

		self._actions = {
			'next': self._nodeNext,
			'previous': self._nodePrevious,
			'in': self._nodeIn,
			'out': self._nodeOut,
			'home': self._home,
			'first': self._nodeFirst,
			'last': self._nodeLast,
			'quit': self._quit
		}

	def run(self):
		try:
			self.display_adapter.refresh(self._context_node, self._highlighted_node)

			while(self._loop is True):
				action = self._input_adapter.read()
				refresh = self._handle(action)
			
				if refresh is True:
					self.display_adapter.refresh(self._context_node, self._highlighted_node)

			self._cleanup()

		except KeyboardInterrupt, SystemExit:
			self._cleanup()
			raise

	def _quit(self):
		self._loop = False

	def _cleanup(self):

		self.display_adapter.cleanup()

	def _handle(self, action):
		if action in self._actions:
			return self._actions[action]()

	def _nodeIn(self):
		refresh = self._highlighted_node.controller(self)

		if len(self._highlighted_node.nodes) > 0:

			self._context_node = self._highlighted_node
			self._highlight_node(self._context_node.nodes[0])

			return True

		return refresh

	def _nodeOut(self):
		if self._context_node.parent is not None:

			self._context_node = self._context_node.parent
			self._highlight_node(self._highlighted_node.parent)

			return True

		return False

	def _nodePrevious(self):
		if(self._highlighted_index > 0):
			self._highlight_node(self._context_node.nodes[self._highlighted_index - 1])

			return True

		return False

	def _nodeFirst(self):
		if(self._highlighted_index > 0):
			self._highlight_node(self._context_node.nodes[0])

			return True
		
		return False

	def _nodeNext(self):
		if(self._highlighted_index < len(self._context_node.nodes) - 1):
			self._highlight_node(self._context_node.nodes[self._highlighted_index + 1])

			return True
		
		return False

	def _nodeLast(self):
		if(self._highlighted_index < len(self._context_node.nodes) - 1):
			self._highlight_node(self._context_node.nodes[len(self._context_node.nodes) - 1])

			return True
		
		return False

	def _home(self):
		self._context_node = self._root_node
		self._highlight_node(self._context_node.nodes[0])

		return True
	
	def _highlight_node(self, node):
		self._highlighted_node = node
		self._highlighted_index = self._context_node.nodes.index(node)

class AdafruitCharLCDDisplay(object):

	def __init__(self, driver, autoscroll=True):
		self.driver = driver
		self._autoscroll = autoscroll
		self.lines = self.driver._lines
		self.cols = self.driver._cols
		self._scroller = None

	def set_feedback_char(self, line, char):
		self.driver.set_cursor(0, line)
		self.driver.write8(ord(char), True)

	def refresh(self, context_node, highlighted_node):

		if self._scroller is not None:
			self._scroller.join()

		self.clear()
		node_count = 0
		highlighted_index = context_node.nodes.index(highlighted_node)

		nodes_to_scroll = []

		for node in context_node.nodes[highlighted_index:]:
			if node_count > self.lines:
				break

			self._print_node(node, node_count, node is highlighted_node)
			nodes_to_scroll.append(node)
			node_count += 1

		if self._autoscroll is True and len(nodes_to_scroll) > 0:
			self._scroller = AdafruitCharLCDScroller(self.driver, nodes_to_scroll)
			self._scroller.start()


	def _print_node(self, node, line, highlight):
		self.driver.set_cursor(1, line)

		if highlight is True:
			self.set_feedback_char(line, '\x3e')

		for char in node.label[:(self.cols - 1)]:
			self.driver.write8(ord(char), True)


	def clear(self):
		self.driver.clear()

	def cleanup(self):
		if self._scroller is not None:
			self._scroller.join()
		
		self.clear()
		
		self.driver.set_backlight(False)
		self.driver.enable_display(False)

class AdafruitCharLCDScroller(threading.Thread):

	def __init__(self, driver, nodes):
		threading.Thread.__init__(self)
		self._driver = driver
		self._nodes = nodes
		self._stop = threading.Event()
		self._cols = self._driver._cols - 1

	def join(self):
		self._stop.set()
		super(AdafruitCharLCDScroller, self).join()

	def run(self):
		time.sleep(0.3)

		nodeOffsets = []
		for node in self._nodes:

			nodeOffsets.append(0)

		while(not self._stop.isSet()):

			for node in self._nodes:

				nodeIndex = self._nodes.index(node)
				labelSlice = node.label[nodeOffsets[nodeIndex]:][:self._cols]
				self._driver.set_cursor(1, nodeIndex)
				
				for char in labelSlice:

					self._driver.write8(ord(char), True)

				if len(node.label) > self._cols:

					self._driver.set_cursor(len(labelSlice) + 1, nodeIndex)

					for space in range(self._cols - (len(labelSlice) -1)):

						self._driver.write8(ord(' '), True)

				nodeOffsets[nodeIndex] += 1

				if len(node.label[nodeOffsets[nodeIndex]:][:self._cols]) < self._cols:

					nodeOffsets[nodeIndex] = 0
			
			time.sleep(0.1)

class ConsoleInput(object):

	def read(self):
		return raw_input('What would you like to do? (previous / next / first / last / in / out / home / quit)\n')


class AdafruitCharLCDKeypadInput(object):

	def __init__(self, driver):
		self._driver = driver

	def read(self):
		if self._driver.is_pressed(AdafruitLCD.UP):
			return 'previous'
		elif self._driver.is_pressed(AdafruitLCD.DOWN):
			return 'next'
		elif self._driver.is_pressed(AdafruitLCD.LEFT):
			return 'out'
		elif self._driver.is_pressed(AdafruitLCD.RIGHT):
			return 'in'
		elif self._driver.is_pressed(AdafruitLCD.SELECT):
			return 'home'










