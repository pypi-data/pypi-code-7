import sys
import os
sys.path.insert(0, os.path.join(__file__, '../../..'))

import nose

from marlowe_ui.tktool import codedoptionmenu

def test_initiate():
    import tkinter as tk
    c = codedoptionmenu.CodedOptionMenu(master=tk.Tk(), options=[(1,'one')])
