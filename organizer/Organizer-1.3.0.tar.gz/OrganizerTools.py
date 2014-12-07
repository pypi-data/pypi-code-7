"""This is a class which contains the classes and functions that I use
to make my Organizer Program work.  It includes a Task class which 
manages details about individual tasks, and an Organizer class which
stores and organizes tasks.  It also has some functions that are
important to making an organizer run.  They are merge() and sort(),
and they are used to implement merge sort in order to sort the tasks in
the organizer.  Version 1.1.0"""

#author: Noah Rossignol
#date: 12/06/2014

#first create a Task class to store the details about tasks
class Task:
    '''Task(name,deadline,priority).  A Task is the essential unit of the organizer.
    each task has a name, deadline, and a priority.  Its methods include a less than function 
    for sorting, a str function to display itself, and a method getName() which returns its name.'''
    def __init__(self,name,deadline,priority):
        self.name=name
        self.displaydeadline=deadline  #will be used in string representation of this task
        l1=deadline.split('/')
        self.deadline=l1
        self.priority=priority
    #task needs a less than method because I will be using merge sort later
    #to organize the organizer
    def __lt__(self,other):
        ''' determines whether self is less than other'''
        if self.deadline[2]==other.deadline[2]:
            if self.deadline[0]==other.deadline[0]:
                if self.deadline[1]==other.deadline[1]:
                    if self.priority==other.priority:
                        return self.name.lower()>other.name.lower()
                    else:
                        return self.priority<other.priority
                else:
                    return self.deadline[1]>other.deadline[1]
            else:
                return self.deadline[0]>other.deadline[0]
        else:
            return self.deadline[2]>other.deadline[2]
    def __str__(self):
        return 'Name: '+self.name+', Deadline: '+self.displaydeadline+', Priority: '+self.priority
    def getName(self):
        return self.name
    def edit(self,value,part):
        if part=='n':
            self.name=value
        elif part=='d':
            self.displaydeadline=value
            l1=value.split('/')
            self.deadline=l1
        elif part=='p':
            self.priority=value

#Now I make an Organizer class to save and organize Tasks.
#It contains a list that will be sorted and displayed later in the program

class Organizer(object):
    '''Organizer object contains a list of Tasks.  Its methods are:
    organizer.getValue(): returns the list of tasks
    organizer.addTask(name,deadline,priority): creates a task and adds it to the list of tasks
    organizer.editTask(task,part,newData):edits the spedified task; it really just passes
    the new data to the spedified task, which has an edit() method of its own.
    organizer.removeTask(name): removes a task with specified name if there is one'''
    def __init__(self):
        self.entries=[]  #the organizer will contain a list of Tasks
    def getValue(self):
        return self.entries
    def addTask(self,name,deadline,priority):
        newTask=Task(name,deadline,priority)
        self.entries.append(newTask)
    def editTask(self,task,part,newData):
        if part=='n':
            task.edit(newData,'n')
        elif part=='d':
            task.edit(newData,'d')
        elif part=='p':
            task.edit(newData,'p')
        elif part=='c':
            pass
    def removeTask(self,task):
        self.entries.remove(task)
