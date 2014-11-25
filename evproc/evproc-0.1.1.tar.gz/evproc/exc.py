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


class EventException(Exception):
    """
    Base class for all ``evproc`` exceptions.
    """

    pass


class ProcessorReregisterException(EventException):
    """
    An exception raised when an attempt is made to register a
    processor with the same name as an already registered processor.
    """

    pass


class IncompatibleRequirementsException(EventException):
    """
    An exception raised when a requirements loop or some other problem
    is detected while topologically sorting event processors prior to
    processing an event.
    """

    pass


class StopProcessing(Exception):
    """
    An exception that may be raised by an event processor to stop
    event processing.
    """

    def __init__(self, retval=None):
        """
        Initialize a ``StopProcessing`` exception.

        :param retval: The return value for ``Processor.process()``.
                       Defaults to ``None``.
        """

        super(StopProcessing, self).__init__('Stop processing')

        self.retval = retval
