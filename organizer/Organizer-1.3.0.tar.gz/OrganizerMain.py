#Organizer
#
#Organizes tasks that need to be done by 
#deadline and priority
#
#author Noah Rossignol
#version 2.2

import cPickle as pickle
#import the tools to make the interface work
from OrganizerTools import Organizer
from OrganizerTools import Task
from OrganizerTools import merge
from OrganizerTools import sort

#This function obtains deadlines and catches erroneous deadlines
def getDeadline():
    while True:
        answer=raw_input("Type the deadline (mm/dd/yyyy): ")
        if answer[3:5]>'31':
            print "Invalid date, enter a valid date in mm/dd/yyyy format."
        elif answer[0:2]>'12':
            print "Invalid month, enter a valid date in mm/dd/yyyy format."
        elif len(answer)==10 and answer[2]=='/' and answer[5]=='/':
            break
        else:
            print "Invalid date.  Enter in mm/dd/yyyy format."
    return answer 

#I will make a function to display the valid commands.
def listCommands():
	print "These are the valid commands: "
	print "    'a': Add a task"
	print "    'd': Display all tasks"
	print "    'e': Edit an existing task" 
	print "    'r': Remove a task"
	print "    'l': List all valid commands"
	print "    'q': Quit" 
#try to open an existing Organizer; if there is none, make one        
try:
    with open('organizer_data.pkl','rb') as input:
        organizer1=pickle.load(input)
except:
    organizer1=Organizer()
    
#Now I make a user interface

print " "
print "Organizer Version 2.2"
print "Noah Rossignol 11/07/2014"
print "-----------------------------"
print "Type l to list all of the valid commands at any time."
listCommands()

while True:
    print " "
    response=raw_input("What would you like to do? ")
    print " "
    
    if response=='q':
		resQ=raw_input("Are you sure you want to quit? (y/n): ")
		if resQ=="y":
			break
    elif response=='d':
        l1=organizer1.getValue()
        l2=sort(l1)
        if len(l2)==0:
			print "There are no tasks currently in the organizer."
        for n in range(len(l2)):
            print l2[n]
    elif response=='a':
        resA1=raw_input("What is the name of the new task? (press 'c' to cancel): ")
        if resA1!='c':
            name=resA1
            deadline=getDeadline()
            priority=raw_input("What priority is this task? (scale of 1-5, 5 being high priority): ")
            organizer1.addTask(name,deadline,priority)
    elif response =='e':
        resC1=raw_input("Which task would you like to edit? (type name of task here or 'c' to cancel): ")
        if resC1!='c':
            flag=False
            for task in organizer1.getValue():
                if task.getName()==resC1:
                    currentTask=task
                    print "Found task with name "+resC1
                    print "This is task "+resC1+": ",
                    print currentTask
                    flag=True
                    break
            if flag==True:
                print "Enter 'n' for name, 'd' for deadline, 'p' for priority or 'c' to cancel. "
                resC2=raw_input("What part of this task would you like to change? ")
                if resC2!='n' and resC2!='d' and resC2!='p' and resC2!='c':
                    print "That is not a valid command.  Enter 'n', 'd', 'p', or 'c'."
                elif resC2!='c':
                    if resC2=='n':
			newName=raw_input("Enter the new name: ")
			organizer1.editTask(currentTask,'n',newName)
		    elif resC2=='d':
			newDate=raw_input("Enter the new deadline: ")
			organizer1.editTask(currentTask,'d',newDate)
		    elif resC2=='p':
			newPriority=raw_input("Enter the new priority: ")
			organizer1.editTask(currentTask,'p',newPriority)
            elif flag==False:
                print 'Could not find task with name '+resC1 
    elif response=='r':
        resB=raw_input("Which task would you like to remove? (type name of task here or 'c' to cancel): ")
        if resB!='c':
			flag=False
			for task in organizer1.getValue():
				if task.getName()==resB:
					print "Found task with name "+resB
					print "This is task "+resB+": ",task
					decision=str(raw_input("Do you want delete it? (y/n)"))
					if decision == "y":
						organizer1.removeTask(task)
						flag=True
						break
			if flag==False:
				print "Could not find task with name "+resB
    elif response=='l':
		listCommands()   
    else:
        print "That is not a valid command.  Enter l for help."

#the last thing to do is to save the organizer
with open("organizer_data.pkl",'wb') as output:
    pickle.dump(organizer1,output,-1)
