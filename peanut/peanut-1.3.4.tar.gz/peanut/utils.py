# -*- coding: utf-8 -*-


__author__ = "Johannes Köster"
__license__ = "MIT"


import sys
import os
import math
import queue
from functools import partial
from collections import namedtuple
from distutils.version import StrictVersion

import numpy as np
import pyopencl as cl
import pyopencl.array as cl_array
import pyopencl.algorithm
from pyopencl.scan import ScanTemplate
from pyopencl.tools import MemoryPool, ImmediateAllocator


class PeanutError(Exception):
    pass


MAXINT = 2 ** 31 - 1
MAXUINT = 2 ** 32 - 1

MIN_GLOBAL_MEM_SIZE_GB =  2.5


def is_higher_version(a, b):
    """Compare two version strings."""
    return StrictVersion(a) > StrictVersion(b)


def to_multiple(n, k):
    """Adjust n to be the smallest multiple of k and bigger than n."""
    return k * math.ceil(n / k)


# taken from algorithm.py of pyopencl
_copy_if_ext_template = partial(ScanTemplate, 
    arguments="item_t *ary, cond_t *cond, item_t *out, scan_t *count",
    scan_expr="a+b", neutral="0",
    output_statement="""
    if (prev_item != item) out[item-1] = ary[i];
    if (i+1 == N) *count = item;
    """,
    template_processor="printf")


class CLDevice:

    _context = dict()

    @classmethod
    def context(cls, cpu=False, min_mem=MIN_GLOBAL_MEM_SIZE_GB * 1024 ** 3):
        if "PYOPENCL_CTX" in os.environ and not cpu:
            return cl.create_some_context()

        device_type = cl.device_type.CPU if cpu else cl.device_type.GPU
        if device_type not in cls._context:
            for platform in cl.get_platforms():
                try:
                    devices = platform.get_devices(device_type=device_type)
                except cl.RuntimeError:
                    continue
                if devices:
                    mem_sizes = [device.get_info(cl.device_info.GLOBAL_MEM_SIZE) for device in devices]
                    devices = [device for device, mem_size in zip(devices, mem_sizes) if mem_size >= min_mem]
                    if not devices:
                        raise PeanutError(
                            "Your system does not provide a {} device with enough memory. "
                            "The largest memory found was {:.2f} GB. "
                            "At least {} GB are required.".format(
                                "CPU" if cpu else "GPU",
                                max(mem_sizes) / 1014 ** 3,
                                MIN_GLOBAL_MEM_SIZE_GB))
                    cls._context[device_type] = cl.Context(devices)
                    return cls._context[device_type]
            raise PeanutError(
                "No OpenCL driver for the {} "
                "installed. "
                "Please install an SDK or appropriate driver.".format(
                "CPU" if cpu else "GPU"))

    def __init__(self, cpu=False):
        self.ctx = self.context(cpu=cpu)
        self.queue = cl.CommandQueue(self.ctx)
        self.cpu = cpu
        self.pool = MemoryPool(ImmediateAllocator(self.queue))
        self.mem_size = self.ctx.get_info(cl.context_info.DEVICES)[0].get_info(cl.device_info.GLOBAL_MEM_SIZE)

    def barrier(self):
        cl.enqueue_barrier(self.queue)

    def arange(self, size, dtype=None):
        return cl_array.arange(self.queue, size, dtype=dtype, allocator=self.pool)

    def copy(self, ndarray):
        return cl_array.to_device(self.queue, ndarray, allocator=self.pool)

    def empty(self, shape, dtype=None):
        return cl_array.empty(self.queue, shape, dtype, allocator=self.pool)

    def empty_like(self, clarray):
        return cl_array.empty_like(clarray)

    def zeros_like(self, clarray):
        return cl_array.zeros_like(clarray)

    def zeros(self, shape, dtype=None):
        return cl_array.zeros(self.queue, shape, dtype, allocator=self.pool)

    def copy_if(self, clarray, predicate):
        clout, clcount, evt = pyopencl.algorithm.copy_if(clarray, predicate)
        count = clcount.get().item()
        del clcount
        return clout[:count]

    def copy_if_ext(self, clarray, clcondition, predicate="cond[i]"):
        knl = _copy_if_ext_template(input_expr=predicate + " ? 1 : 0").build(
            clarray.context,
            type_aliases=(
                ("scan_t", np.int32),
                ("item_t", clarray.dtype),
                ("cond_t", clcondition.dtype)))
        clout = cl.array.zeros_like(clarray)
        clcount = self.empty((), dtype=np.int32)
        evt = knl(clarray, clcondition, clout, clcount, queue=self.queue)
        count = clcount.get().item()
        del clcount
        return clout[:count]

    def compile(self, *names, options="", **constants):
        source = ""
        for name in names:
            sourcepath = os.path.join(
                os.path.dirname(__file__),
                '{}.cl'.format(name))
            with open(sourcepath) as f:
                source += f.read() % constants
        program = cl.Program(self.ctx, source)
        try:
            program.build(options="-cl-mad-enable " + options)
            setattr(self, name, program)
        except Exception as e:
            print(e, file=sys.stderr)
            raise e

    def log(self):
        return self.program.get_build_info(self.ctx.devices[0],
            cl.program_build_info.LOG)
