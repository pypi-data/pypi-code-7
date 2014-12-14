#!/usr/bin/env python
import user, decida
from decida.Calc import Calc
from Tkinter import *

root=Tk()
fl=Frame(root, bd=10, relief=RAISED, bg="red")
fr=Frame(root, bd=10, relief=RAISED, bg="blue")
fl.pack(side=LEFT)
fr.pack(side=RIGHT)
Calc(fl, wait=False)
Calc(fr, wait=True)
