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

import abc

import six


class Namespace(object):
    """
    A class containing attributes, stored in a dictionary.
    """

    def __init__(self):
        """
        Initialize a ``Namespace`` object.
        """

        super(Namespace, self).__setattr__('_data', {})

    def __getattr__(self, name):
        """
        Retrieve a value from a namespace.

        :param name: The name of the item to retrieve.

        :returns: The value of the requested item.
        """

        # Reject internal attributes and those that don't exist
        if name.startswith('_') or name not in self._data:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (self.__class__.__name__, name))

        # Return the desired data
        return self._data[name]

    def __setattr__(self, name, value):
        """
        Set a value on a namespace.

        :param name: The name of the item to set.
        :param value: The value to set the item to.
        """

        # Reject internal attributes
        if name.startswith('_'):
            raise AttributeError("can't set internal attribute")

        self._data[name] = value

    def __delattr__(self, name):
        """
        Delete a value from a namespace.

        :param name: The name of the item to delete.
        """

        # Reject internal attributes and those that don't exist
        if name.startswith('_'):
            raise AttributeError("can't delete internal attribute")
        elif name not in self._data:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (self.__class__.__name__, name))

        del self._data[name]


class ProcessorData(object):
    """
    A class containing namespaces into which processors can store
    data.  Data cannot be stored into any other attributes of an
    instance of ``ProcessorData``, to encourage processors to use
    namespaces.
    """

    def __init__(self):
        """
        Initialize a ``ProcessorData`` object.
        """

        super(ProcessorData, self).__setattr__('_namespaces', {})

    def __getattr__(self, name):
        """
        Retrieve a namespace.

        :param name: The name of the namespace to retrieve.

        :returns: The namespace associated with that name.
        """

        # Reject internal attributes
        if name.startswith('_'):
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (self.__class__.__name__, name))

        # Create a namespace if necessary
        if name not in self._namespaces:
            self._namespaces[name] = Namespace()

        return self._namespaces[name]

    def __setattr__(self, name, value):
        """
        Set a namespace.  This is prohibited.

        :param name: The name of the namespace to set.
        :param value: The value to set the attribute to.
        """

        raise AttributeError("can't set attribute")

    def __delattr__(self, name):
        """
        Delete a namespace.  This is prohibited.

        :param name: The name of the namespace to delete.
        """

        raise AttributeError("can't delete attribute")


@six.add_metaclass(abc.ABCMeta)
class Event(object):
    """
    Represent an event.  Event processors will be passed an instance
    of a subclass of the ``Event`` class.
    """

    def __init__(self, ctxt=None):
        """
        Initialize an event.

        :param ctxt: Optional extra data needed by event processors.
                     This data could be used to specify an execution
                     context.
        """

        self.ctxt = ctxt
        self._proc = ProcessorData()

    @property
    def proc(self):
        """
        A namespaced storage location for processor-specific data.
        Processors can store their data on attributes of the
        namespaces.
        """

        return self._proc

    @abc.abstractproperty
    def name(self):
        """
        A name describing the event.  Must be unique.  This name can be
        used by processors to filter which events those processors are
        interested in.
        """

        pass  # pragma: no cover
