import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import tkinter as tk

from marlowe_ui.tktool.codedoptionmenu import CodedOptionMenu

app = tk.Tk()

option1 = [(1, 'one'), (2, 'two'), (3, 'three'), (0, 'zero')]
option2 = [(9, 'nine'), (8, 'eight'), (7, 'seven'), (6, 'six')]
option = option1
menu = CodedOptionMenu(app, option)

# can I change the property menu?
menu.config(width=30, anchor='e')
menu.pack()

def set_action():
    menu.set(0)
set_btn = tk.Button(app, text='set', command=set_action)
set_btn.pack()

def get_action():
    print(menu.get())
get_btn = tk.Button(app, text='get', command=get_action)
get_btn.pack()

def switch_action():
    global option
    if option == option1:
        option = option2
    else:
        option = option1
    menu.set_new_option(option)

switch_btn = tk.Button(app, text='switch', command=switch_action)
switch_btn.pack()

app.mainloop()
