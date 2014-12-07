'''This is a graphical user interface for my organizer.  It uses the 
same set of tools that other versions of Organizer have used, but has
a GUI.  The tools come from OrganizerTools.py.'''

#author Noah Rossignol
#version 1.4.0
#date 12/06/2014

from Tkinter import *
from OrganizerTools import *
import tkMessageBox
import Tkinter
import cPickle as pickle

#try to get an existing organizer
try:
    with open('organizer_data.pkl','rb') as input:
        organizer1=pickle.load(input)
except:
    organizer1=Organizer()

#many functions need to be defined in this interface
def updateList():
	'''Updates the list of tasks in the main window'''
	l1=organizer1.getValue()
	l2=sorted(l1, reverse=True)
	#first I have to clear the existing list
	L.delete(0,L.size())
	for n in range(len(l2)):	
		entry=l2[n].__str__()
		L.insert(n, entry)
	L.pack

#Make menu functions
def adder():
	'''adds a task to the organizer'''
	addFrame=Toplevel()
	addFrame.transient(top)
	addFrame.title("Add")
	label1=Label(addFrame, text="Name")
	label1.grid(row=0, column=0)
	E1=Entry(addFrame)
	E1.grid(row=0, column=1)
	#second field
	label2=Label(addFrame, text="Deadline (mm/dd/yyyy)")
	label2.grid(row=1, column=0)
	E2=Entry(addFrame)
	E2.grid(row=1, column=1)
	#third field
	label3=Label(addFrame, text="Priority (scale 1-5)")
	label3.grid(row=2, column=0)
	E3=Entry(addFrame)
	E3.grid(row=2, column=1)
	def addOK():
		organizer1.addTask(E1.get(),E2.get(),E3.get())
		updateList()
		addFrame.withdraw()
	B=Button(addFrame, text="OK", command=addOK)
	B.grid(row=3, column=1)

def editor():
	editFrame=Toplevel()
	editFrame.transient(top)
	editFrame.title("Edit")
	try:
		l1=organizer1.getValue()
		l2=sorted(l1, reverse=True)
		currentindex=L.curselection()[0]
		currentTask=l2[currentindex]
	except IndexError:
		editFrame.withdraw()
		tkMessageBox.showinfo(title="Error", message="No task is selected")
	#I will use radio buttons to select which part to edit
	#I need a function for those buttons to call
	def sel():
		selection="New "+str(var.get())+":"
		eLabel.config(text=selection)
	eLabel=Label(editFrame, text="Editor")
	var=StringVar()
	R1=Radiobutton(editFrame, text="Name", variable=var, value="Name",command=sel)
	R1.pack(anchor=W)
	R2=Radiobutton(editFrame,text="Deadline",variable=var,value="Deadline",command=sel)
	R2.pack(anchor=W)
	R3=Radiobutton(editFrame,text="Priority",variable=var,value="Priority",command=sel)
	R3.pack(anchor=W)
	eLabel.pack(side=LEFT)
	newValue=Entry(editFrame)
	newValue.pack(side=RIGHT)
	def editOK():
		if var.get()=="Name":
			organizer1.editTask(currentTask, 'n', newValue.get())
			updateList()
			editFrame.withdraw()
		elif var.get()=="Deadline":
			organizer1.editTask(currentTask, 'd', newValue.get())
			updateList()
			editFrame.withdraw()
		elif var.get()=="Priority":
			organizer1.editTask(currentTask, 'p', newValue.get())
			updateList()
			editFrame.withdraw()
		else:
			tkMessageBox.showinfo(title="Error", message="No part is selected")
	askOk=Button(editFrame, text="OK", command=editOK)
	askOk.pack(side=RIGHT)
	
	
def remover():
	try:
		l1=organizer1.getValue()
		l2=sorted(l1, reverse=True)
		currentindex=L.curselection()[0]
		currentTask=l2[currentindex]
		Flag=tkMessageBox.askokcancel(title="Remove", message="Are sure you want to remove this task?")
		if Flag:
			organizer1.removeTask(currentTask)
			updateList()
			tkMessageBox.showinfo(message="Task Removed")
		else:
			tkMessageBox.showinfo(message="Cancelled")
	except IndexError:
		tkMessageBox.showinfo(message="No task is selected.")

def quitter():
	flag=tkMessageBox.askokcancel(title="Quit", message="Save and quit?")
	if flag:
		with open("organizer_data.pkl",'wb') as output:
			pickle.dump(organizer1,output,-1)
		top.quit()

def helper():
	tkMessageBox.showinfo(title="Help", message="Contact me at noahrossignol@yahoo.com")

#Create a menubar to display options
top=Tk()
top.title("Organizer G")
menubar=Menu(top)
menubar.add_command(label="Add", command=adder)
menubar.add_command(label="Edit", command=editor)
menubar.add_command(label="Remove", command=remover)
menubar.add_command(label="Quit", command=quitter)
menubar.add_command(label="Help", command=helper)

#Create a listbox to display tasks
scroller=Scrollbar(top)
scroller.pack(side=RIGHT, fill=Y)

L=Listbox(top, yscrollcommand=scroller.set, width=50)
l1=organizer1.getValue()
l2=sorted(l1, reverse=True)
for n in range(len(l2)):
	entry=l2[n].__str__()
	L.insert(n, entry)
L.pack()

top.config(menu=menubar)
top.mainloop()
