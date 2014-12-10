# -*- coding: utf-8 -*-
import os


class RecordFileError(Exception):
    "Base Exception for block files."


class RecordFile(object):
    """Low level fixed-size record file.
       Record numbers are zero-based.
    """

    def __init__(self, fname, blocksize=4, overwrite=False):
        """Initialize a new RecordFile object.

            :param fname:  string
            :param overwrite: bool (True overwrite existing file)
        """
        self.fname = fname
        if hasattr(fname, 'strpath'):
            self.fname = fname.strpath
        self.blocksize = blocksize
        self.overwrite = overwrite

        if not fname:
            raise RecordFileError("Missing file name.")
        if blocksize < 2:
            raise RecordFileError("Block size must be greater than 2 bytes.")

        self.fp = self.open(self.fname, overwrite)

    def __repr__(self):  # pragma: no cover
        return '\n'.join(list(self))

    def __str__(self):
        return ''.join(list(self))

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()

    def count(self):
        """Return number of records in the fils.
        """
        return self._eof() / self.blocksize

    def goto_recnum(self, n):
        """Position the file at record `n`, if `n` == -1, then go to
           the end of the file (writing then becomes appending).
           It is possible to go past the end of the file and write a record,
           causing the file to grow.
        """
        if n == -1:
            self.fp.seek(0, 2)
        else:
            self.fp.seek(n * self.blocksize, 0)

    def truncate(self, recnum=None):
        "Truncate the file at `recnum` (ie. `recnum` will be gone)."
        if recnum is not None:
            self.goto_recnum(recnum)
        self.fp.truncate()

    def goto_recnum_relative(self, n):
        """Advance forward or backward (negative `n`) `n` records.
        """
        self.fp.seek(n * self.blocksize, 1)

    def goto_first_record(self):
        "Go to start of first record."
        self.fp.seek(0, 0)

    def goto_last_record(self):
        "Go to the starting position of the last record."
        self.goto_recnum(len(self) - 1)

    def read(self):
        "Read a block at the current position."
        return self.fp.read(self.blocksize)

    def write(self, data, flush=True):
        "Write data to file at current position."
        if len(data) != self.blocksize:
            raise RecordFileError(
                "Tried to write data (%d) which " % len(data) +
                "didn't fit in blocksize (%d)." % self.blocksize)
        self.fp.write(data)
        if flush:
            self.fp.flush()

    def _eof(self):
        "Return the position at the end of the file"
        self.fp.seek(0, 2)
        eof = self.fp.tell()
        return eof

    @property
    def curpos(self):
        "Return the current position."
        return self.fp.tell() / self.blocksize

    def __iter__(self):
        "Yield all records."
        eof = self._eof()
        self.goto_first_record()
        while self.fp.tell() < eof:
            data = self.read()
            yield data

    def __len__(self):
        "Returns the number of records in the file."
        return self.count()

    def __getitem__(self, n):
        "Get record number `n`."
        self.goto_recnum(n)
        return self.read()

    def __setitem__(self, n, data):
        "Set record number `n`."
        self.goto_recnum(n)
        data = data if isinstance(data, list) else [data]
        for rec in data:
            self.write(rec)

    def swap(self, a, b):
        "Swap records at positions `a` and `b`."
        self[a], self[b] = self[b], self[a]

    def __delitem__(self, n):
        """Move record to the end of the file, then truncate the file.
        """
        length = len(self) - 1
        self.swap(n, length)
        self.truncate(length)

    def open(self, fname, overwrite):
        "Open or create the file."
        if overwrite:
            fp = self.create_new_file(fname)
        else:
            try:
                fp = self.open_existing_file(fname)
            except IOError as e:
                if not (e.errno == 2 and
                        e.strerror == 'No such file or directory'):
                    raise  # pragma: no cover
                fp = self.create_new_file(fname)
        return fp

    def open_existing_file(self, fname):
        "Open the file for read and write if possible."
        if os.access(fname, os.W_OK):
            fp = open(fname, 'r+b')
        else:
            fp = open(fname, 'rb')
        return fp

    def create_new_file(self, fname):
        """Create a new keystore file (overwriting/deleting any existing file.

           Args:
              fname (str):   Filename to use.

           Returns:
              (file):        The created file.
              
        """
        return open(fname, 'w+b')

    def close(self):
        "Close file and write statusrec."
        self.fp.flush()
        self.fp.close()

    def __del__(self):
        try:
            self.close()
        except:
            pass
