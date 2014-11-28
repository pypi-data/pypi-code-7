# -*- coding: utf-8 -*-
'''
Created on Nov 14, 2014

Nixtla (time lapse): Framework for Sign Language Lexical Recognition

@author: curiel
'''

import sys
import os

sys.path.insert(1, os.path.abspath('..'))

from nixtla.core.tools.guis.qt_gui import StartQT

StartQT(sys.argv)