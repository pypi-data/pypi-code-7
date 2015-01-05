#Validation
TIMELOG_NOT_IN_CONFIG = '''\
Taskwarrior Timesheets does not work without a user defined attribute 
totaltime. In your .taskrc please put these two parameters: 
uda.totaltime.type=string
uda.totaltime.label=Total Time\
'''

WORKLOG_NOT_IN_CONFIG = '''\
Taskwarrior Timesheets does not work without a user defined attribute 
worklog. In your .taskrc please put these two parameters: 
uda.worklog.type=string
uda.worklog.label=Work Log\
'''

#Logging
LOGGED_TIME = 'You logged %s for a total of %s'
