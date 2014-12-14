#!/usr/bin/env python
import user, decida, string
from decida.spice_value import spice_value

nums = string.split("1.23G 1A 1FF 1MEG 1.2M 23K")
for num in nums:
    print num, spice_value(num)
