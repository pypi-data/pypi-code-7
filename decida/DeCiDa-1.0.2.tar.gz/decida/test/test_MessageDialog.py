#!/usr/bin/env python
import user, decida
from decida.MessageDialog import *
from decida.messagebox import *
from Tkinter import *
from tkMessageBox import *

message="""
    Four score and seven years ago our fathers brought forth on
    this continent, a new nation, conceived in Liberty, and
    dedicated to the proposition that all men are created
    equal. Now we are engaged in a great civil war, testing
    whether that nation, or any nation so conceived and so
    dedicated, can long endure. We are met on a great
    battle-field of that war. We have come to dedicate a
    portion of that field, as a final resting place for those
    who here gave their lives that that nation might live. It
    is altogether fitting and proper that we should do this.
"""
if False :
    if not Tkinter._default_root :
        root = Tk()
        root.wm_state("withdrawn")
    root.option_add("*Message*font", "Courier 20 bold", 80)
    root.option_add("*Label*font", "Courier 20 bold", 80)
    root.option_add("*Text*font", "Courier 20 bold", 80)
    root.option_add("*Entry*font", "Courier 20 bold", 80)
    root.option_add("*Entry*background", "orange", 80)
    root.option_add("*Text*background", "orange", 80)
    root.option_add("*Label*background", "orange", 80)
    root.option_add("*Message*background", "orange", 80)
    root.option_add("*Dialog.msg.font", "Courier 12 normal", 100)
    root.option_add("*Dialog.msg.width", "10i", 100)
    root.option_add("*Dialog.dtl.font", "Courier 20 bold", 100)
    tkMessageBox.showinfo(parent=root, message=message, detail="hello")

if True :
    MessageDialog(title="Random Info", message=message, bitmap="info")
