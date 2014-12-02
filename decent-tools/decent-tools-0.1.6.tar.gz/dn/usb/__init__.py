import sys as _sys
import common

if _sys.platform.startswith("darwin"):
    from macosx import is_kernel_driver_active, detach_kernel_driver, attach_kernel_driver
elif _sys.platform.startswith('linux'):
    from linux import is_kernel_driver_active, detach_kernel_driver, attach_kernel_driver
else:
    raise Exception("Sorry. Only mac and linux are supported")
