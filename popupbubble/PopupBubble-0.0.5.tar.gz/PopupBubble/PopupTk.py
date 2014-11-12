#!/usr/bin/env python3

from tkinter import *

class PopupTk(Frame):
    def __init__(self, master=None, title="Notification", msg="New information", duration=2):
        Frame.__init__(self, master)
        self.duration = duration

        # setup button
        close_button = Button(self, text="C", command=self.master.destroy)
        close_button.pack(side=LEFT)

        # setup text labels
        title_label = Label(self, text=title, wraplength=250, width=255)
        title_label.config(justify=LEFT, anchor="w", borderwidth=1, relief="solid", font=("Arial", 12, "bold"))
        title_label.pack(fill=X, expand=True)
        msg_label = Label(self, text=msg, wraplength=250, width=255, height=80)
        msg_label.config(justify=LEFT, anchor="w", borderwidth=1, relief="solid")
        msg_label.pack(fill=X, expand=True)

        self.pack(side=TOP, fill=BOTH, expand=YES, padx=10, pady=10)

        # get screen width and height
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        w = 300
        h = 100
        # calculate position x, y
        x = ws - w
        y = hs - h
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.master.overrideredirect(True)
        self.master.lift()

    def auto_close(self):
        msec_until_close = self.duration * 1000
        self.master.after(msec_until_close, self.master.destroy)

def poptk(msg, title="Notification", duration=3):
    root = Tk()
    sp = PopupTk(root, title=title, msg=msg, duration=duration)
    sp.auto_close()
    root.call('wm', 'attributes', '.', '-topmost', True)
    root.mainloop()

if __name__ == '__main__':
    poptk("hi there!")
    print("I am here!")


