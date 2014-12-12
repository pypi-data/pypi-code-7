import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import tkinter as tk

from marlowe_ui.tktool.truncatedentry import TruncatedEntry

app = tk.Tk()

lentry = TruncatedEntry(app, limitwidth=10)
lentry.pack()

def val_lentry():
    print(lentry.validate())

def get_lentry():
    print(lentry.get())

btn_validate = tk.Button(app, text='validate', command=val_lentry)
btn_validate.pack()

btn_get = tk.Button(app, text='get', command=get_lentry)
btn_get.pack()

app.mainloop()
