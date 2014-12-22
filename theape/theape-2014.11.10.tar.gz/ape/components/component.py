
# python standard library
from abc import abstractmethod, ABCMeta
import inspect
import os

# this package
from ape import BaseClass
from ape import ApeError

from ape.infrastructure.strings import RESET
from ape.infrastructure.strings import BOLD
from ape.infrastructure.crash_handler import try_except
from ape.infrastructure.errors import ConfigurationError
from ape.infrastructure.code_graphs import module_diagram, class_diagram
from ape.parts.countdown.countdown import TimeTracker


DOCUMENT_THIS = __name__ == '__builtin__'


class Component(BaseClass):
    """
    A base-class for Composite and Leaf
    """
    __metaclass__ = ABCMeta
    def __init__(self):
        """
        Component Constructor
        """
        super(Component, self).__init__()
        self._logger = None
        return

    @abstractmethod
    def __call__(self):
        """
        abstractmethod that will be the main invocation when implememented
        """
        return

    @abstractmethod
    def check_rep(self):
        """
        abstract: Representation-check called by composite

        :raise: ConfigurationError if representation invalid
        """
        return

    @abstractmethod
    def close(self):
        """
        abstractmethod: called for Keyboard Interrupts to allow file-closing
        """
        return        


class Composite(Component):
    """
    A Composite to hold and execute Components
    """
    def __init__(self, error=None, error_message=None,
                 identifier=None,
                 component_category=None,
                 time_remains=None):
        """
        Composite Constructor

        :param:

         - `error`: Exception to catch when calling components
         - `error_message`: string for header of error messages
         - `component_category`: label for error messages when reporting component actions
         - `identifier`: something to identify this when it starts the call
         - ``time_remains`` - a TimeTracker or CountdownTimer
        """
        super(Composite, self).__init__()
        self.error = error
        self.error_message = error_message
        self.identifier = identifier
        self.component_category = component_category
        self._logger = None
        self._components = None
        self._time_remains = time_remains
        return

    @property
    def components(self):
        """
        The list of components
        """
        if self._components is None:
            self._components = []
        return self._components

    @property
    def time_remains(self):
        """
        :return: TimeTracker (default) or CountdownTimer object
        """
        if self._time_remains is None:
            self._time_remains = TimeTracker()
        return self._time_remains

    @time_remains.setter
    def time_remains(self, countdown):
        """
        Sets the time_remains attribute

        :param:

         - ``countdown``: a CountdownTimer to call
        """
        self._time_remains = countdown
        return

    def add(self, component):
        """
        appends the component to self.components

        :param:

         - `component`: A Component

        :postcondition: component appended to components
        """
        # using is instead of in in case __eq__ overriden
        for existing_component in self.components:
            if component is existing_component:
                return
        self.components.append(component)
        return

    def remove(self, component):
        """
        Removes the component from the components (if it was there)
        """
        try:
            self.components.remove(component)
        except ValueError as error:
            self.logger.debug(error)
        return

    def __iter__(self):
        """
        Iterates over the components
        """
        for component in self.components:
            yield component

    def __len__(self):
        """
        Counts the components

        :return: count of components
        """
        return len(self.components)

    def __getitem__(self, index):
        """
        gets slice or index of components
        """
        return self.components[index]

    @try_except
    def one_call(self, component):
        """
        Calls the  component (pulled out into a method to catch the exceptions)

        :raise:

         - `ApeError` if component is not callable
        """
        if not hasattr(component, '__call__'):
            raise ApeError(("'{0}' has not implemented the __call__ interface. " 
                            "What a way to run a railroad.").format(component.__class__.__name__))
        component()
        return

    def __call__(self):
        """
        The main interface -- starts components after doing a check_rep

        """
        self.logger.debug("{b}** Checking the Composite Class Representation **{r}".format(b=BOLD,
                                                                                          r=RESET))

        self.check_rep()
        count_string = "{b}** {l} {{c}} of {{t}} ('{{o}}') **{r}".format(b=BOLD, r=RESET,
                                                                         l=self.component_category)

        self.logger.info("{b}*** {c} Started ***{r}".format(b=BOLD, r=RESET,
                                                             c=self.identifier))
        
        total_count = len(self.components)
        
        self.logger.info("{b}*** Starting {c} ***{r}".format(b=BOLD, r=RESET,
                                                             c=self.component_category))

        # the use of time-remains is meant to facilitate repeated re-use of the same component calls
        while self.time_remains():
            for count, component in enumerate(self.components):
                self.logger.info(count_string.format(c=count+1,
                                                     t=total_count,
                                                     o=str(component)))                                                 
                self.one_call(component)
            
        self.logger.info("{b}*** {c} Ended ***{r}".format(b=BOLD, r=RESET,
                                                             c=self.identifier))        
        return

    def check_rep(self):
        """
        Checks the representation invariant     

        :raise: ConfigurationError
        """
        try:
            # these checks only make sense when used in the infrastructure
            # at some point this should be generalized somehow so it can act like a
            # composite proper
            assert inspect.isclass(self.error),(
                "self.error must be an exception, not {0}".format(self.error))
            assert issubclass(self.error, Exception),(
                "self.error needs to be an exception, not {0}".format(self.error))
            assert self.error_message is not None, (
                "self.error_message must not be None")
            assert self.component_category is not None, (
                "self.component_category must not be None")

            # check all your children
            for component in self.components:
                if hasattr(component, 'check_rep'):
                    component.check_rep()
                else:
                    self.log_error(error="'{0}' hasn't implemented the 'check_rep' method.".format(component.__class__.__name__),
                                    message="Thanks for the sour persimmons, cousin.")

        except AssertionError as error:
            raise ConfigurationError(str(error))
        return

    def close(self):
        """
        calls the `close` method on each component

        :postcondition: comuponents closed and self.components is None
        """
        for component in self.components:
            if hasattr(component, 'close'):
                component.close()
            else:
                self.logger.warning("'{0}' hasn't implemented the 'close' method. We hate him.".format(component))
        self._components = None
        return

    def __str__(self):
        return ("{2} -- Traps: {0}, "
                "{3} Components: {1}").format(self.error.__name__,
                                         self.component_category,
                                         self.__class__.__name__,
                                         len(self.components))
        
#end class Composite
