#!/usr/bin/env python3

from tkinter import *
from tkinter import messagebox

root = Tk()

################################################################
### A Label that grows itself
################################################################
# class GrowLabel(Label):
#     def __init__(self, master):
#         Label.__init__(self, master)
#         self.counter = 12
#         self.config(text=str(self.counter), fg="blue", font=("verdana", self.counter, "bold"))
#         self.pack()
#         button = Button(self.master, text="Stop", command=self.master.destroy)
#         button.pack()
#
#     def count(self):
#         self.counter += 1
#         self.config(text=str(self.counter), fg="blue", font=("verdana", self.counter, "bold"))
#         self.after(1000, self.count)
#
# label = GrowLabel(root)
# label.count()


################################################################
### Group of check buttons
################################################################
# like_coffee = IntVar()
# like_tea = IntVar()
# like_coffee.set(0)
# like_tea.set(0)
#
# def showChoice():
#     print("%d %d" % (like_coffee.get(), like_tea.get()))
#
# Checkbutton(root, text="Coffee", variable=like_coffee, command=showChoice).grid(row=0, sticky=W)
# Checkbutton(root, text="Tea",    variable=like_tea,    command=showChoice).grid(row=1, sticky=W)

# class Checkbar(Frame):
#     def __init__(self, parent=None, picks=[], side=LEFT, anchor=W):
#         # super(Checkbar, self).__init__(parent)
#         Frame.__init__(self, parent)
#         self.vars = []
#         for pick in picks:
#             var = IntVar()
#             chk = Checkbutton(self, text=pick, variable=var)
#             chk.pack(side=side, anchor=anchor, expand=YES)
#             self.vars.append(var)
#
#     def state(self):
#         return [var.get() for var in self.vars]
#
# lng = Checkbar(root, ["Python", "Perl", "C++", "Ruby"])
# tgl = Checkbar(root, ["English", "French"])
# lng.pack(side=TOP, fill=X)
# tgl.pack(side=LEFT)
# lng.config(relief=GROOVE, bd=3)
#
# def allstates():
#     print(lng.state())
#     print(tgl.state())
#
# Button(root, text="Quit", command=root.quit).pack(side=RIGHT)
# Button(root, text="Peek", command=allstates).pack(side=RIGHT)

# def show_entry_fields():
#     s = "First name: %s\nLast name: %s" % (e1.get(), e2.get())
#     print(s)
#     messagebox.showinfo(title="Info", message=s)
#
# Label(root, text="First name").grid(row=0)
# Label(root, text="Last name").grid(row=1)
# e1 = Entry(root)
# e2 = Entry(root)
# e1.grid(row=0, column=1)
# e2.grid(row=1, column=1)
# Button(root, text="Quit", command=root.quit).grid(row=3, sticky=W, pady=1)
# Button(root, text="Show", command=show_entry_fields).grid(row=3, column=1, sticky=W, pady=1)

################################################################
### A name-job form
################################################################
# fields = ["Last name", "First name", "Job", "Country"]
# def makeForm(root, fields):
#     entries = []
#     for field in fields:
#         row = Frame(root)
#         label = Label(row, width=15, text=field, anchor=W)
#         entry = Entry(row)
#         row.pack(fill=X, padx=5, pady=5)
#         label.pack(side=LEFT)
#         entry.pack(side=RIGHT, expand=YES, fill=X)
#         entries.append((field, entry))
#     return entries
#
# def fetch(entries):
#     info_strings = []
#     for entry in entries:
#         info_strings.append("%s: '%s'" % (entry[0], entry[1].get()))
#     info_string = "\n".join(info_strings)
#     messagebox.showinfo(title="Info", message=info_string)

# entries = makeForm(root, fields)
# root.bind("<Return>", lambda event, e=entries: fetch(e))
# b1 = Button(root, text="Show", command=(lambda e=entries: fetch(entries)))
# b1.pack(side=LEFT, padx=5, pady=5)
# b2 = Button(root, text="Quit", command=root.quit)
# b2.pack(side=LEFT, padx=5, pady=5)



################################################################
### A calculator (expression evaluator)
################################################################
# from math import *
#
# res = Label(root)
#
# def evaluate(event):
#     res.config(text="Result: " + str(eval(entry.get())))
#     entry.delete(0, END)
#     entry.focus_set()
#
# entry = Entry(root)
# entry.bind("<Return>", evaluate)
# entry.pack()
# res.pack()


################################################################
### Solve the unknown
################################################################
# class App:
#     def __init__(self, root):
#         self.fields = ["A", "B", "AB"]
#         self.root = root
#         self.entries = []
#         self.numerics = []
#         self.makeRows()
#         button_frame = Frame(self.root)
#         Button(button_frame, text="Run", command=self.run).pack(side=RIGHT)
#         Button(button_frame, text="Reset", command=self.reset).pack(side=RIGHT)
#         button_frame.grid(row=3, column=1, sticky=E)
#         root.bind("<Return>", lambda e: self.run())
#         root.bind("<space>", lambda e: self.reset())
#
#     def makeRows(self):
#         for i in range(len(self.fields)):
#             label = Label(self.root, text=self.fields[i], justify=LEFT)
#             entry = Entry(self.root)
#             label.grid(row=i, sticky=W)
#             entry.grid(row=i, column=1)
#             self.entries.append(entry)
#
#     def getValues(self):
#         try:
#             values = [e.get() for e in self.entries]
#             self.numerics = [float(v) if v!="" else v for v in values]
#             print(self.numerics)
#         except ValueError:
#             messagebox.showerror(title="Error", message="Input only numerical values!")
#             self.numerics = []
#
#     def checkEmpty(self, elem):
#         if elem == "":
#             return 1
#         else:
#             return 0
#
#     def checkEmptyInEntries(self):
#         if len(self.numerics) != 0:
#             entry_emptiness = [self.checkEmpty(v) for v in self.numerics]
#             if sum(entry_emptiness) != 1:
#                 messagebox.showerror(title="Error", message="Leave one and only one entry empty!")
#                 return None
#             return entry_emptiness
#         else:
#             return None
#
#     def run(self):
#         self.getValues()
#         emptiness = self.checkEmptyInEntries()
#         if emptiness == None:
#             return None
#         empty_index = emptiness.index(1)
#         if empty_index == 0:
#             self.entries[0].delete(0, END)
#             self.entries[0].insert(0, str(self.numerics[2] / self.numerics[1]))
#         elif empty_index == 1:
#             self.entries[1].delete(0, END)
#             self.entries[1].insert(0, str(self.numerics[2] / self.numerics[0]))
#         else:
#             self.entries[2].delete(0, END)
#             self.entries[2].insert(0, str(self.numerics[0] * self.numerics[1]))
#
#     def reset(self):
#         for entry in self.entries:
#             entry.delete(0, END)
#
# app = App(root)


################################################################
### Paint with canvas
################################################################
# canvas_width = 500
# canvas_height = 100
#
# def paint(event):
#     python_gree = "#476042"
#     x1, y1 = (event.x - 1), (event.y - 1)
#     x2, y2 = (event.x + 1), (event.y + 1)
#     canvas.create_oval(x1, y1, x2, y2)
#
# canvas = Canvas(root, width=canvas_width, height=canvas_height)
# canvas.pack(expand=YES, fill=BOTH)
# canvas.bind("<B1-Motion>", paint)
# msg = Label(root, text="Press and drag")
# msg.pack()

def msg():
    messagebox.showinfo(title="Info", message="How are you?")

# canvas_width = 80
# canvas_height = 40
# canvas = Canvas(root, width=canvas_width, height=canvas_height)
# canvas.pack()
# y = int(canvas_height / 2)
# canvas.create_line(0, y, canvas_width, y, fill="#229922")
# grape_gif='''R0lGODlhIAAgALMAAAAAAAAAgHCAkC6LV76+vvXeswD/ANzc3DLNMubm+v/6zS9PT6Ai8P8A//// /////yH5BAEAAAkALAAAAAAgACAAAAS00MlJq7046803AF3ofAYYfh8GIEvpoUZcmtOKAO5rLMva 0rYVKqX5IEq3XDAZo1GGiOhw5rtJc09cVGo7orYwYtYo3d4+DBxJWuSCAQ30+vNTGcxnOIARj3eT YhJDQ3woDGl7foNiKBV7aYeEkHEignKFkk4ciYaImJqbkZ+PjZUjaJOElKanqJyRrJyZgSKkokOs NYa2q7mcirC5I5FofsK6hcHHgsSgx4a9yzXK0rrV19gRADs='''
# gif_image = PhotoImage(data=grape_gif)
# button = Button(root, image=gif_image, command=msg)
# button.pack()


# def poptk():
#     setCloseButton(root)
#     root.call('wm', 'attributes', '.', '-topmost', True)
# def setCloseButton(master):
#     img_b64 = """R0lGODlhGAAYAPEAADIyMjMzMzQ0NAAAACH5BAEAAAMALAAAAAAYABgAAAJOnI8Ciu0I4gKvtmXzidoKBXbQBE5iVJZYJpGkQlluisYVnYbVgk/+XcOBBMAebWecFWfMR1Lo+DCNjuD0JcpqZUPmFSbjrbYDGJF8YGQKADs="""
#     img = PhotoImage(data = img_b64)
#     master.config(padx=5, pady=5)
#     close_button = Button(master, image=img, command=master.destroy)
#     # close_button = Button(master, text="x", command=master.destroy)
#     close_button.pack(side=LEFT)
# poptk()

# img_b64 = """R0lGODlhGAAYAPEAADIyMjMzMzQ0NAAAACH5BAEAAAMALAAAAAAYABgAAAJOnI8Ciu0I4gKvtmXzidoKBXbQBE5iVJZYJpGkQlluisYVnYbVgk/+XcOBBMAebWecFWfMR1Lo+DCNjuD0JcpqZUPmFSbjrbYDGJF8YGQKADs="""
# img = PhotoImage(data = img_b64)
# close_button = Button(root, image=img, command=root.quit)
# close_button.pack(side=LEFT)
# root.mainloop()

# def poptk(root):
#     img_b64 = """R0lGODlhGAAYAPEAADIyMjMzMzQ0NAAAACH5BAEAAAMALAAAAAAYABgAAAJOnI8Ciu0I4gKvtmXzidoKBXbQBE5iVJZYJpGkQlluisYVnYbVgk/+XcOBBMAebWecFWfMR1Lo+DCNjuD0JcpqZUPmFSbjrbYDGJF8YGQKADs="""
#     img = PhotoImage(data = img_b64)
#     close_button = Button(root, image=img, command=root.quit)
#     close_button.pack(side=LEFT)
# poptk(root)
# root.mainloop()

from PIL import ImageTk
img_b64 = """R0lGODlhGAAYAPEAADIyMjMzMzQ0NAAAACH5BAEAAAMALAAAAAAYABgAAAJOnI8Ciu0I4gKvtmXzidoKBXbQBE5iVJZYJpGkQlluisYVnYbVgk/+XcOBBMAebWecFWfMR1Lo+DCNjuD0JcpqZUPmFSbjrbYDGJF8YGQKADs="""
img_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00(\x00\x00\x00(\x08\x06\x00\x00\x00\x8c\xfe\xb8m\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00\tpHYs\x00\x00\r\xd7\x00\x00\r\xd7\x01B(\x9bx\x00\x00\x00\x19tEXtSoftware\x00www.inkscape.org\x9b\xee<\x1a\x00\x00\x00ItEXtCopyright\x00Public Domain http://creativecommons.org/licenses/publicdomain/Y\xc3\xfe\xca\x00\x00\x03\nIDATX\x85\xc5\x98Ok\x13A\x1c\x86\xdf\xdfdCkB\x0b\x96\xb6\xe2A\xab\x88\x95*-t\xb3\x84\xd0\xe4"XD{\xd0\x83\x17\x15O\x1e\xfb\r\xc4\xa3_\xc3\xa3\x9e<\xe8)\x07\xbdY\x8b\x84$\xf5R,zS\x10\n\x9e*\xd6l\xdc\xcc\xeb\xc1\xb4&\xd9\x7f\xc9\xfe\x89\x0f\xece\xe67\xf3>\xd9\xd9Y2+$\x11\x85\xb5\xb5\xb5\x13\xb6m_\x13\x91S\x00f{.\x00\xf8~t\x91\xdc\x9f\x98\x98x\xb3\xbd\xbd\xfd+J\x8e\x11\xc9\x0e\x80m\xdb\x97E\xe4\x81O\xf7\xd9\xee\x05\x11\x81m\xdb\xdf\x004\xa2\xe4\xa8\x88~p\x1cg\x8fd\'\xac\x8ed\xc7q\x9c\xbd\xa89\x12u\x89\x01`uu\xf5\xa2a\x18%\xadu\xb1\xbb\xd4\xbdb\xfbJ\xa9\x9a\xe38\xefwvv>\xff\x17\xc1#*\x95\xcaT\xab\xd5z\xda\xdb699\xf9pkk\xebG\xdc\xb9#/q/\x07\x07\x07\xaeg\xd9\xab-\n\xb1\xee`\xa5R\x99:<<<\xa3\x94Z\x04po\xa0\xfb\xb9\xd6\xfaS.\x97\xfb\x1a\xe7N\x8e,\xd8\x95**\xa5\xca\x00\xae\x00\x90\x90!\x04\xb0\xab\xb5~\x97\xcb\xe5j\xa3\xca\x0e-("\xca4\xcd\xdb"r\x07\xd1_O\x0e\xc9\x17\xcdf\xf3%I\x9d\x98\xa0eYY\x00\x8f\x01,E\x14\x1b\xe4#\x80\'\xf5z\xfdwX\xe1P\x9bDD\xee"99\x00X\xea\xce\x19J\xa8\xa0eY\xcb$7\xe2;\xf5Cr\xc3\xb2\xac\xe5\xb0\xba@A\x11Q$7\x11\xbe\x11\xa2 $7E$\xd0!\xb0\xb3X,.\x88\xc8L\xb2^\xff\x10\x91\x99b\xb1\xb8\x10T\x13(\xe88\xce\xa5d\x95F\xcf\x08[\xe2\xd4\x05\xc32\xc26\xc9b\x82.\x912|\x05WVVN\x02\x98K\\\xc7\xcd\\7\xcb\x13_\xc1l6\x9b\xfa\xf2\x0e\x93\xe5+8\x8e\xe7o\x98\xac \xc1\xf3\xe9\xe8\x8c\x96\xe5+H2\xf0\xfd\x94$AY\x9e\x82\xa6i\xce\x01\xc8\xa7f\xe4&\xdf\xcdt\xe1)h\x18\xc6\xb9TuF\xc8\xf4\x14\xd4Z{\x16\xa7\x89_\xa6\xa7 I\xcf\xe24\xf1\xcb\xf4\x14TJ\x8dm\x83\x84e\xba\x04K\xa5\xd24\xc9\xf9\xf4\x95\xfa!9_*\x95\xa6\x07\xdb]\x82\x9dN\xe7\xeax\x94\xdcxe\xf7\t\x8a\x88\x00X\x1f\x9b\x91\x9b\xf5\xae\xc31}\xa73\xd34+$\xf3\x00~\x02\x80\x88\x10\x00\xb4\xd6\xae\x93\xd5Q\x1f\xfe\x1e+\x83\x10\x00 \xe9\xfaW\xae\x94\xea\xeb#\x997M\xb3\x02\xe0\xed\xf1\xe0$>}\xa4\x89\x94\xcb\xe5)\xdb\xb6\x0b\x83\x1d^\xbfx\x98\x9aa\xc6\x01\x80a\x18}u^\xe3\xb2\xd9l\xc3h\xb5Z\x8f\x00\\\x18f\xd2A\x06\x1e\x17\xdf6/\xb4\x0e?\xb7\xb7\xdb\xed\xeb\n\xc0\xe9Q\xc5\xc6\xc8\xacA\xf2\xb5\x88\xdc\x8c2ZD2$\xc3\x8e\r\x0e\x80v\x94\xf9IVcm\x92B\xa1p_Dn\x85\x84\xbcj4\x1a\xcf\xa2f\xc4\xfa>\x98\xc9d>$Q\x13D,\xc1Z\xad\xb6K\xb2\xea\xd7O\xb2Z\xab\xd5v\xe3d$\xf2\x1e4M\xd3RJ\xdd@\xf7\xcb>\x80/Z\xebj\xb3\xd9\xac\xc7\x9d\xfb\x0f\x18\x8c-O\x8e\xe7)\x89\x00\x00\x00\x00IEND\xaeB`\x82'
img = ImageTk.PhotoImage(data=img_bytes)
Label(root, image=img).place(x=10, y=20)
Button(root, text="Relative").place(relx=0.5, rely=0.5)

root.mainloop()
