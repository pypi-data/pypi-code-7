from jsonschema import validate, ValidationError
import threading
import time
import sys


class Db():
    """
    A simple key-value data store.

    Attributes:
        debug (bool, default=False): Enable or disable console logging
        schema (dict, default=None): JSON schema to check data against
        data (dict): Dictionary where data is stored
        credits (str): Some silly ASCII art
        lock (_thread.lock): Handles concurrent reads / writes to the data store
    """

    def __init__(self, debug=False, schema=None):
        """
        Creates a new data store.

        Args:
            debug (bool, default=False): Enable or disable console logging
            schema (dict, default=None): JSON schema to check data against

        Raises:
            TypeError: If `debug` is not a bool
        """

        if type(debug) is not bool:
            raise TypeError('debug must be True or False')
        else:
            self.debug = debug
            self.schema = schema
            self.data = {}
            self.credits = """
                              __
                       ___~~~`  `~~__
                 ___~~~              `~_
                |~_                     `~_
                |  ~_               ___ ~~ |
                |    ~_        __~~~       |
                |      ~_ __~~~            |
                |        |                 |
                |        |                 |
                ~_       |       bx        |
                  ~_     |               __|
                    ~_   |          __~~~
                      ~_ |     __~~~
                        ~|__~~~

                (c) 2015 tylucaskelley
            """
            self.lock = threading.Lock()

    def put(self, key, val, timeout=None):
        """
        Put a value in the data store, with an optional expiration time (in ms).

        Args:
            key: Name of value
            val: Data to store
            timeout (int or float, default=None): Lifetime of data (in ms)

        Raises:
            ValidationError: If `val` does not fit the schema (if schema exists)
            ValueError: If `timeout` is provided but is not a number
        """

        with self.lock:
            if self.schema:
                validate(val, self.schema)

            ms, death = None, None
            if timeout:
                ms = float(timeout) / 1000.0
                death = int(round(time.time() * 1000)) + ms

            item = {
                'value': val,
                'exp': death
            }

            if ms and ms > 0:
                threading.Timer(ms, self.delete, [key]).start()

            self.data[key] = item

    def check(self, val):
        """
        Check to see if data fits the schema.

        Args:
            val: Data to validate

        Returns:
            bool: True if value fits, False otherwise
        """

        with self.lock:
            if self.schema:
                try:
                    validate(val, self.schema)
                except ValidationError:
                    return False
            return True

    def get(self, key):
        """
        Get a value from the data store.

        Args:
            key: Key to get

        Returns:
            Value associated with `key`

        Raises:
            KeyError: If key is not found
        """

        with self.lock:
            return self.data[key]['value']

    def mget(self, *keys):
        """
        Get multiple values from the data store.

        Args:
            *keys: Arbitrary number of keys to get.

        Returns:
            dict: Dictionary of values
        """

        with self.lock:
            return {k: v['value'] for k, v in self.data.items() if k in keys}

    def delete(self, key):
        """
        Delete a value from the data store.

        Args:
            key: Key to delete

        Returns:
            The deleted value

        Raises:
            KeyError: If `key` is not found
        """

        with self.lock:
            self.data.pop(key)

    def mdelete(self, *keys):
        """
        Delete multiple values from the data store.

        Args:
            *keys: Arbitrary number of keys to delete

        Raises:
            KeyError: If a key that doesn't exist is passed in
        """

        for k in keys:
            self.delete(k)

    def clear(self):
        """Empty the data store."""

        with self.lock:
            self.data = {}

    def all(self):
        """
        Get everything from the data store, excluding expiration times.

        Returns:
            dict: Dictionary of all key-value pairs in the data store
        """

        with self.lock:
            return {k: v['value'] for k, v in self.data.items()}

    def keys(self):
        """
        Get a list of the keys in the data store.

        Returns:
            list: A list of the keys in the data store
        """

        with self.lock:
            return list(self.data.keys())

    def vals(self):
        """
        Get a list of the values in the data store.

        Returns:
            list: A list of the values in the data store
        """

        with self.lock:
            return [v['value'] for k, v in self.data.items()]

    def size(self):
        """
        Get the size in bytes of the data store.

        Returns:
            int: The number of bytes that the data store takes up
        """

        with self.lock:
            return sys.getsizeof(self.data)

    def exp(self, key):
        """
        Get the expiration date of an item in the data store.

        Args:
            key: Key to get expiration date of

        Returns:
            float: The expiration date of the key

        Raises:
            KeyError: If the key isn't found
        """

        with self.lock:
            return self.data[key]['exp']

    def __len__(self):
        """
        Get the number of items in the data store.

        Returns:
            int: Number of keys in the data store
        """

        with self.lock:
            return len(self.data)

    def __str__(self):
        """
        Get a string representation of the data store.

        Returns:
            str: A string representation of the data store
        """

        with self.lock:
            return str(self.data)
