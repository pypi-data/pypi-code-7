
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
from ape import DontCatchError
from ape.components.component import Composite
from ape.parts.storage.filestorage import FileStorage
from ape import FILE_TIMESTAMP


# the singletons will be kept in this dictionary
singletons = {}


class SingletonEnum(object):
    """
    A holder for singleton names
    """
    __slots__ = ()
    composite = 'composite'
    filestorage = 'filestorage'


def get_composite(name, error=DontCatchError, error_message=None,
                  identifier=None, component_category='unknown'):
    """
    Gets a Composite Singleton

    :param:

     - `name`: name to register singleton (clients that want same singleton, use same name)
     - `error`: exception to catch (``DontCatchError`` default)
     - `error_message`: message to log on catching the error
     - `identifier`: an identifier for the component (for logging, etc.)
     - `component_category`: classifier for Composite.components

    :return: Composite singleton
    """
    if SingletonEnum.composite not in singletons:
        singletons[SingletonEnum.composite]  = {}
    if name not in singletons[SingletonEnum.composite]:
        if error_message is None:
            error_message = "{0} component error".format(name)
        if identifier is None:
            identifier = name
            
        singletons[SingletonEnum.composite][name] = Composite(error=error,
                                                              error_message=error_message,
                                                              identifier=identifier,
                                                              component_category=component_category)
    return singletons[SingletonEnum.composite][name]


def get_filestorage(name, path=None, 
                    timestamp=FILE_TIMESTAMP):
    """
    Gets a FileStorage Singleton

    :param:

     - `name`: name to register singleton (clients that want same singleton, use same name)

     - `path`: path to prepend to all files (default is current directory)
     - `timestamp`: strftime format to timestamp file-names

    :return: Composite singleton
    """
    if SingletonEnum.filestorage not in singletons:
        singletons[SingletonEnum.filestorage]  = {}
    if name not in singletons[SingletonEnum.filestorage]:
        singletons[SingletonEnum.filestorage][name] = FileStorage(path=path,
                                                                  timestamp=timestamp)
    return singletons[SingletonEnum.filestorage][name]


def refresh():
    """
    Clears the `singletons` dictionary
    """
    singletons.clear()
    return
