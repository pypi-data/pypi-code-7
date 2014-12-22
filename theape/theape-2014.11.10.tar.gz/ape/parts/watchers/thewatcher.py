
# The MIT License (MIT)
# 
# Copyright (c) 2013 Russell Nakamura
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# this package
from ape import BaseThreadClass
from ape import ApeError
from ape.parts.eventtimer import wait
from ape.parts.eventtimer import EventTimer


class TheWatcher(BaseThreadClass):
    """
    A watcher of wifi information
    """
    def __init__(self, query, storage, fields, use_header=True, interval=1,
                 separator=',', use_timestamp=True, timestamp=None):
        """
        TheWatcher constructor

        :param:

         - `query`: A query (e.g. IwconfigQuery)
         - `storage`: a file-like (thread-safe) object to write output to
         - `fields`: a list of attribute-names for the query object
         - `use_header`: if True, saves field-names as header before data starts
         - `interval`: seconds between queries
         - `separator`: token to separate fields in the data output
         - `use_timestamp`: if true first column of data will be timestamp
         - `timestamp`: timestamp format (strftime format) (uses storage.timestamp if None)
        """
        super(TheWatcher, self).__init__()
        self.query = query
        self.storage = storage
        self.fields = fields
        self.stopped = False
        self.use_header = use_header
        self.interval = interval
        self.separator = separator
        self.use_timestamp = use_timestamp
        self._timestamp = timestamp
        self. _header = None
        self._timer = None
        return

    @property
    def timestamp(self):
        """
        :return: strftime string format for datetime
        """
        if self._timestamp is None:
            self._timestamp = self.storage.timestamp
        return self._timestamp

    @property
    def timer(self):
        """
        An event timer for the ``wait`` decorator to keep time
        """
        if self._timer is None:
            self._timer = EventTimer(seconds=self.interval)
        return self._timer

    @property
    def header(self):
        """
        :return: fields joined by separator to use as first line of data output
        """
        if self._header is None:
            self._header = self.separator.join(self.fields)
            if self.use_timestamp:
                self._header = 'timestamp' + self.separator + self._header
        return self._header
    
    def __call__(self):
        """
        The main interface. starts the thread
        """
        self.logger.debug('Starting the TheWatcher')
        self.stopped = False
        self.thread.name = self.__class__.__name__
        self.thread.start()
        return

    def check_rep(self):
        """
        Checks that the querier has the fields passed in
        """
        try:
            for field in self.fields:
                assert hasattr(self.query, field)
        except AssertionError:
            raise ApeError("Unknown attribute (field) '{0}' for '{1}'".format(field,
                                                                              self.query.__class__.__name__))
        return

    @wait
    def log_data(self):
        """
        Gets the field-data from the query and sends to storage
        """
        line = self.separator.join((getattr(self.query, field) for field in self.fields))
        if self.use_timestamp:
            line = self.separator.join((datetime.datetime.now().strftime(self.timestamp),
                                        line))
        self.storage.writeline(line)


    def run(self):
        """
        The method to be called by the BaseThreadClass' run_thread
        """
        if self.use_header:
            self.storage.writeline(self.header)

        while not self.stopped:
            self.log_data()
        return

    def stop(self):
        """
        :postcondition: self.stopped is True
        """
        self.stopped = True
        return

    def close(self):
        """
        sets stopped to true, closes storage
        """
        self.stopped = True
        self.storage.close()
        return
# end class TheWatcher
