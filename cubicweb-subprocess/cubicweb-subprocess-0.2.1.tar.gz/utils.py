# -*- coding: utf-8 -*-
# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-subprocess utilities"""


from Queue import Queue
from threading import Thread


def communicate(process, chunk_size=4096):
    """function generator that send events when contents are available in
    the outputs of the ``process``.

    Each time data is available from the process outputs, it copies
    the data into ``stdout`` or ``stderr`` and yield the correponding
    object.

    :process: process-like object
    :stdout | stderr: file-like object that will collect stdout | stderr
    :chunk_size: maximum size of content to read at a time (default 1 word)
    :yield: ``stdout`` or ``stderr`` object depending on available content
    """
    queue = Queue()
    def _pipe_reader(name, pipe):
        try:
            for content in iter(lambda: pipe.readline(chunk_size), b''):
                queue.put((name, content))
        finally:
            queue.put((name, None))
    thread_stdout = Thread(target=_pipe_reader, args=('stdout', process.stdout))
    thread_stderr = Thread(target=_pipe_reader, args=('stderr', process.stderr))
    thread_stdout.start()
    thread_stderr.start()
    nb_threads = 2
    while nb_threads:
        name, content = queue.get()
        if content is None: # not more to read
            nb_threads -= 1
            continue
        yield name, content
    thread_stdout.join()
    thread_stderr.join()
