import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import tkinter as tk

from marlowe_ui.tktool import validateentry
from marlowe_ui.tktool.oneof import OneofFactory

app = tk.Tk()

# element class
class Elem(tk.Frame):
    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)

        self.w = validateentry.Double(self)

        self.w.pack()

        self.clear()

    def set(self, d):
        self.w.set(d)

    def get(self):
        return self.w.get()

    def clear(self):
        self.set(0)

    def validate(self):
        return self.w.validate()

    def enable(self):
        self.w.config(state=tk.NORMAL)

    def disable(self):
        self.w.config(state=tk.DISABLED)


C = OneofFactory(Elem, 1)

gui = C(app)
gui.pack(side=tk.TOP)

# test buttons
testframe = tk.Frame(app)
# set default
def set_action():
    gui.set([1, 2, 3, 4, 5, 6])
setbtn = tk.Button(testframe, text='set example', command=set_action)
setbtn.pack(side=tk.LEFT, pady=2)
# get
def get_action():
    print(gui.get())
getbtn = tk.Button(testframe, text='get', command=get_action)
getbtn.pack(side=tk.LEFT, pady=2)
# clear
def clear_action():
    gui.clear()
clearbtn = tk.Button(testframe, text='clear', command=clear_action)
clearbtn.pack(side=tk.LEFT, pady=2)
# validate
def validate_action():
    print(gui.validate())
getbtn = tk.Button(testframe, text='validate', command=validate_action)
getbtn.pack(side=tk.LEFT, pady=2)

# enable
def enable_action():
    gui.enable()
enablebtn = tk.Button(testframe, text='enable', command=enable_action)
enablebtn.pack(side=tk.LEFT, pady=2)

# disable
def disable_action():
    gui.disable()
disablebtn = tk.Button(testframe, text='disable', command=disable_action)
disablebtn.pack(side=tk.LEFT, pady=2)

testframe.pack(side=tk.TOP)

app.mainloop()
