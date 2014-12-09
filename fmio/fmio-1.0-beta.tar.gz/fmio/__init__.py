#!/usr/bin/env python3

import argparse
import gzip
import queue
import struct
import sys
from collections import namedtuple
from enum import Enum

import numpy as np
import pandas as pd

class CompressionType(Enum):
    none = 1
    gzip = 2

class DataType(Enum):
    f16 = 1
    f32 = 2
    f64 = 3

DTYPE_MAP = {
        DataType.f16: (np.float16,2),
        DataType.f32: (np.float32,4),
        DataType.f64: (np.float64,8)
}
MAGIC_NUMBER = 0x759e7c08
ENCODING = "ascii"
_header_fields = [
    "magic",
    "n_columns",
    "max_key_size",
    "compression_type",
    "dtype"
]
Header = namedtuple("HeaderType", _header_fields)
HEADER_SIZE = len(_header_fields * 4)
HEADER_LAYOUT = "<" + "L" * len(_header_fields)

def encode_string(x,sz):
    return x.encode(ENCODING).ljust(sz, b"\0")

def decode_string(handle,sz):
    s = handle.read(sz)
    return s[:s.find(b"\0")]

class Base(object):
    def __enter__(self):
        return self

    def __exit__(self, *ex):
        self.close()

    def close(self):
        self.handle.close()

class Reader(Base):
    QUEUE_SIZE = 100

    def __init__(self, handle, array=False):
        #self.handle = gzip.open(handle, "rb")
        self.handle = handle
        self.array = array

        self.header = Header._make(struct.unpack(HEADER_LAYOUT,
            self.handle.read(HEADER_SIZE)))
        assert self.header.magic == MAGIC_NUMBER, \
            "File format not recognized"

        self.dtype, self.dtype_size \
                = DTYPE_MAP[DataType(self.header.dtype)]

        stype = "|S"+str(self.header.max_key_size)
        self.columns = pd.Index(
                np.char.decode(
                    np.fromstring(self.handle.read(self.header.max_key_size * self.header.n_columns),
                        dtype=stype,
                        count=self.header.n_columns),
                    "ascii"))
        self.rtype = np.dtype([("key", stype), ("data", self.dtype, self.header.n_columns)])
        self._data = None
        self._eof = False
        self._read()

    def __iter__(self):
        return self

    def _read(self):
        if self._data is not None:
            if len(self._data) or self._eof:
                return
            if not len(self._data) and self._eof:
                return
        s = self.handle.read(self.rtype.itemsize * self.QUEUE_SIZE)
        assert len(s) % self.rtype.itemsize == 0
        n = int(len(s) / self.rtype.itemsize)
        self._eof = n < self.QUEUE_SIZE
        self._data = np.fromstring(s, count=n, dtype=self.rtype)

    def __next__(self):
        if len(self._data) == 0:
            if self._eof:
                raise StopIteration
            self._read()
        o, self._data = self._data[0], self._data[1:]
        k = o["key"].decode("ascii")
        data = o["data"]
        return k,data

        """
        name = decode_string(self.handle,
                self.header.max_key_size)
        data = self.handle.read(self.header.n_columns \
                * self.dtype_size)
        if len(data) == 0:
            raise StopIteration
        data = np.fromstring(data, dtype=self.dtype, count=len(self.columns))
        if self.array:
            return name, data 
        else:
            o = pd.Series(data, index=self.columns)
            o.name = name
            return o
        """

    def to_frame(self):
        self.array = True
        X = pd.DataFrame.from_dict(dict(self)).T
        X.columns = self.columns
        return X

class Writer(Base):
    def __init__(self, handle, columns, dtype=np.float16,
            max_key_size=25):
        #self.handle = gzip.open(handle, "wb", compresslevel=1)
        self.handle = handle

        try:
            dtype_e = [k for k,(t,s) in DTYPE_MAP.items() 
                    if t==dtype][0]
        except IndexError:
            raise Exception("dtype %s not suppported" % dtype)

        self.header = Header._make((MAGIC_NUMBER,
            len(columns), max_key_size,
            CompressionType.none.value, dtype_e.value))

        self.dtype, self.dtype_size \
                = DTYPE_MAP[DataType(self.header.dtype)]
        self.max_key_size = max_key_size
        self.nc = len(columns)

        self.handle.write(struct.pack(HEADER_LAYOUT, *self.header))
        for c in columns:
            self.handle.write(encode_string(c,max_key_size))

    def put(self, name, data):
        assert len(name) <= self.max_key_size
        assert len(data) == self.nc
        self.handle.write(encode_string(name,
            self.max_key_size))
        if not data.dtype != self.dtype:
            data = np.array(data, dtype=self.dtype)
        self.handle.write(data.tostring())

def serialize(f_in=sys.stdin,
        f_out=sys.stdout.buffer,
        dtype=np.float32,
        verbose=False,
        delimiter="\t"):
    assert "b" not in f_in.mode
    assert "b" in f_out.mode

    columns = next(sys.stdin).rstrip("\n").split("\t")[1:]
    nc = len(columns)
    with Writer(sys.stdout.buffer, columns, dtype=dtype) as w:
        for i,line in enumerate(sys.stdin):
            if verbose and (i % 100 == 0):
                print("fmio:", i, "records processed", file=sys.stderr)
            pos = line.find("\t")
            key = line[:pos]
            data = np.fromstring(line[pos+1:], 
                    dtype=dtype,
                    count=nc, sep="\t")
            w.put(key,data)

def deserialize(f_in=sys.stdin.buffer,
        f_out=sys.stdout, 
        verbose=False,
        delimiter="\t"):
    assert "b" in f_in.mode
    assert "b" not in f_out.mode

    rdr = Reader(f_in, array=True)
    print("", *rdr.columns, sep=delimiter, file=f_out)
    for i,(name, data) in enumerate(rdr):
        if verbose and (i % 100 == 0):
            print("fmio:", i, "records processed", file=sys.stderr)
        print(name, *np.round(data.astype(np.float32),3), 
                sep=delimiter, file=f_out)
        #data.tofile(sys.stdout, format="%0.3f", sep="\t")

def main():
    from signal import signal, SIGPIPE, SIG_DFL
    signal(SIGPIPE,SIG_DFL) 

    p = argparse.ArgumentParser()
    # For compatibility with other "compressors"; 
    #   it always outputs to stdout
    p.add_argument("-c", action="store_true")
    p.add_argument("--deserialize", "-d",
            action="store_true")
    p.add_argument("--verbose", "-v",
            action="store_true")
    args = p.parse_args()

    if args.deserialize:
        deserialize(verbose=args.verbose)
    else:
        serialize(verbose=args.verbose)

if __name__ == "__main__":
    main()
