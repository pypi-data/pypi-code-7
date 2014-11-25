# Copyright 2014 Rackspace
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the
#    License. You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing,
#    software distributed under the License is distributed on an "AS
#    IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#    express or implied. See the License for the specific language
#    governing permissions and limitations under the License.

import stevedore

from evproc import exc


def _topo_sort(nodes):
    """
    Performs a topological sort of a specified set of nodes.

    :param nodes: A ``set`` containing instances of ``ProcNode`` to be
                  topologically sorted.

    :returns: An iterator providing a topological sort of the
              designated nodes.  Beyond the guarantee of topological
              sorting, no ordering guarantees are made.
    """

    # The set of nodes we've emitted so far
    emitted = set()

    while nodes:
        # Find one node that doesn't require any others (except nodes
        # already emmitted)
        for node in nodes:
            if not (node.reqs - emitted):
                break
        else:
            # Couldn't find a node with no requirements
            raise exc.IncompatibleRequirementsException(
                'Could not find a processor for event; possible '
                'requirements loop.  Processors left: "%s"' %
                '", "'.join(sorted(n.name for n in nodes)))

        # Yay, we found a node!
        nodes.remove(node)
        emitted.add(node)
        yield node


class ProcNode(object):
    """
    A class representing single event processors.
    """

    def __init__(self, proc, name):
        """
        Initialize a ``ProcNode`` instance.

        :param proc: The ``Processor`` instance to use to look up
                     dependent processors.
        :param name: The name of the processor.
        """

        # Save the processor and the name
        self.proc = proc
        self.name = name

        # Func is late-binding
        self._func = None

        # Set up the filters
        self.filters = []

        # Set up the requirements set
        self.reqs = set()

    def __hash__(self):
        """
        Make the ``ProcNode`` instance hashable.

        :returns: A hash value for the ``ProcNode`` instance.
        """

        return hash(self.name)

    def __eq__(self, other):
        """
        Test whether this ``ProcNode`` instance is equal to another.

        :param other: The other ``ProcNode`` instance to compare to.

        :returns: A ``True`` value if this ``ProcNode`` and the one
                  specified by ``other`` are equal, ``False``
                  otherwise.
        """

        return self.name == other.name

    def __ne__(self, other):
        """
        Test whether this ``ProcNode`` instance is not equal to another.

        :param other: The other ``ProcNode`` instance to compare to.

        :returns: A ``False`` value if this ``ProcNode`` and the one
                  specified by ``other`` are equal, ``True``
                  otherwise.
        """

        return self.name != other.name

    def __call__(self, ev):
        """
        Call the processor function.

        :param ev: The event to pass to the processor.

        :returns: The return value of the processor function.
        """

        return self._func(self.proc, ev)

    def check(self, ev):
        """
        Test whether a given event is to be processed by this
        ``ProcNode``.

        :param ev: The ``Event`` instance to filter against.

        :returns: A ``True`` value if the processor wants the event
                  ``ev``, ``False`` otherwise.
        """

        return (not self.filters) or any(filt(ev) for filt in self.filters)

    @property
    def func(self):
        """
        Retrieve the processor function implementing the event processor.
        """

        return self._func

    @func.setter
    def func(self, value):
        """
        Set the value of the processor function.  This may be done only
        once.

        :param value: The value to set the processor function to.
        """

        # Only allow one set
        if self._func is not None:
            raise AttributeError("can't set attribute")

        # Save the function first
        self._func = value

        # Set up the filters
        self.filters = getattr(value, '_ev_filters', [])

        # Resolve requirements
        for req_name in getattr(value, '_ev_requires', set()):
            # Get the requirement
            req = self.proc._get(req_name)

            # Save it as a requirement
            self.reqs.add(req)

        # Resolve any required_by values
        for req_name in getattr(value, '_ev_required_by', set()):
            # Get the requirement
            req = self.proc._get(req_name)

            # Save ourself as a requirement of it
            req.reqs.add(self)


class Processor(object):
    """
    A class representing a complex event processor.  Instances of this
    class contain the graph of event processors, and are responsible
    for coordinating the actual processing of an event in the order
    required by the graph.
    """

    def __init__(self):
        """
        Initialize a ``Processor``.
        """

        self.nodes = {}

        # A cache for the topological sort algorithm
        self.topo_cache = {}

    def _get(self, proc_name):
        """
        Retrieve a ``ProcNode`` instance corresponding to the given
        processor name.  If the node does not exist yet, it will be
        created.

        :param proc_name: The name of the individual processor.

        :returns: An instance of ``ProcNode``.
        """

        # Generate a ProcNode if we need it
        if proc_name not in self.nodes:
            self.nodes[proc_name] = ProcNode(self, proc_name)

        return self.nodes[proc_name]

    def _get_procs(self, ev):
        """
        Generate and return a topologically sorted list of processors for
        processing an event.

        :param ev: The event to be processed.

        :returns: A list of ``ProcNode`` objects, in a topologically
                  sorted order.
        """

        # Build a set of processors
        nodes = set(node for node in self.nodes.values() if node.check(ev))

        # Assemble the cache key
        key = frozenset(node.name for node in nodes)

        # Do we need to perform a topological sort?
        if key not in self.topo_cache:
            self.topo_cache[key] = list(_topo_sort(nodes))

        # Return the list of processors
        return self.topo_cache[key]

    def register(self, proc, name=None):
        """
        Register a function as an event processor.

        :param proc: The function to be registered.  This function
                     will be called with two arguments to process an
                     event; the first argument will be this
                     ``Processor`` instance, and the second argument
                     will be the ``Event`` instance describing the
                     event.
        :param name: The name of the event processor function, for
                     dependency resolution.  If not provided, the
                     function name will be used.
        """

        # Select the processor name
        if not name:
            name = proc.__name__

        # Look up the appropriate ProcNode
        node = self._get(name)

        # If the function has already been registered, we must bail
        # out
        if node.func is not None:
            raise exc.ProcessorReregisterException(
                'Processor "%s" has already been registered' % name)

        # OK, register the function
        node.func = proc

        # Invalidate the topo_cache
        self.topo_cache = {}

    def load_from(self, namespace):
        """
        Load event processors from a designated entrypoint namespace.

        :param namespace: The namespace for the entrypoints
                          designating event processors.  Each
                          entrypoint should be a function taking two
                          arguments, that will be called to process
                          every event.  The first argument will be
                          this ``Processor`` instance, and the second
                          argument will be the ``Event`` instance
                          describing the event.
        """

        # Generate a stevedore manager
        mgr = stevedore.ExtensionManager(namespace)

        # Now, register each extension
        for ext in mgr:
            self.register(ext.plugin, ext.name)

    def process(self, ev):
        """
        Process an event.  All defined and interested processors will be
        called in an order consistent with the requirements defined on
        those processors.

        :param ev: The event to process.

        :returns: Returns ``None``, or a value passed to a
                  ``StopProcessing`` exception raised by a processor.
        """

        # Walk through all the processors and process the event
        for proc in self._get_procs(ev):
            try:
                proc(ev)
            except exc.StopProcessing as ex:
                return ex.retval

        return None
