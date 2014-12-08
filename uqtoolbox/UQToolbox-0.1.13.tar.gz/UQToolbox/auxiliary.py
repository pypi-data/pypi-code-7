# -*- coding: utf-8 -*-

#
# This file is part of UQToolbox.
#
# UQToolbox is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# UQToolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with UQToolbox.  If not, see <http://www.gnu.org/licenses/>.
#
# DTU UQ Library
# Copyright (C) 2014 The Technical University of Denmark
# Scientific Computing Section
# Department of Applied Mathematics and Computer Science
#
# Author: Daniele Bigoni
#

__all__ = ['object_store']

import os
import cPickle as pkl
import shutil

def object_store(path,obj):
    """ Used to store any object in the library.

    :param string path: path pointing to the location where to store the data
    :param object obj: a pickleable object

    """
    if os.path.isfile(path):
        # If the file already exists, make a safety copy
        shutil.copyfile(path, path+".old")
    ff = open(path,'wb')
    pkl.dump(obj,ff)
    ff.close()
