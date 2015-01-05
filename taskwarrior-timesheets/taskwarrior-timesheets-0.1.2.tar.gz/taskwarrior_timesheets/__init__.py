#!/usr/bin/env python
import sys
import os
import json
import datetime
import re
import messages
import iso8601
import time
from tempo.api import TEMPO, TempoError
from tempo.utils import find_jira_issue_key
from utils import date_handler, DateTimeEncoder, has_totaltime_uda, has_worklog_uda,\
  tempo_timesheets_enabled, tty_input, seconds_to_jira_hours, load_config, tty_output,\
  round_time, ceil_datetime
from prettytable import PrettyTable
from dateutil import parser, relativedelta
from dateutil.tz import tzlocal
from taskw import TaskWarrior

#TODO I need to get rid of seconds completely and just round up to minutes, or possibly just do it when 
#just logging time to timesheets.
tw = TaskWarrior();

class TaskTimesheetsError(Exception):

  def __init__(self, text):
      return super(TaskTimesheetsError, self).__init__(text) 

def main():
  config = load_config();
  original = json.loads(sys.stdin.readline());
  modified = json.loads(sys.stdin.readline());
  to_return = None

  regexp = re.compile(r'worklog = True')
  if regexp.search(modified['description']) is not None:
    to_return = worklog_report(original, modified, config)
  else:
    to_return = log_time(original, modified, config)
  
  sys.stdout.write(to_return)

def log_time(original, modified, config):
  data_path = config['data']['location']

  if ('start' not in original and 'start' in modified):
    if (has_totaltime_uda(config) and has_worklog_uda(config)):
      print("Starting logging time");

  elif ('start' in original and 'start' not in modified):
    if (has_totaltime_uda(config) and has_worklog_uda(config)):
      round_minutes = 1
      if 'timesheets' in config:
          if 'rounding' in config['timesheets']:
              round_minutes = int(config['timesheets']['rounding'])

      start = ceil_datetime(parser.parse(original['start']), round_minutes*60)
      end = ceil_datetime(datetime.datetime.now(tzlocal()), round_minutes*60)
      duration = end - start
      current_readable = seconds_to_jira_hours(duration.seconds, False)
      file_is_empty = os.stat(os.path.expanduser(data_path + '/worklog.data')).st_size == 0

      with open(os.path.expanduser(data_path + '/worklog.data'), 'a+') as f:
          #Find the latest worklog for this uuid and get the last work log with that uuid 
          last_worklog = None
          lastline = None
          regexp = re.compile(r'\"uuid\": \"%s\"' % modified['uuid'])
          
          for line in f.readlines():
              if regexp.search(line) is not None:
                  last_worklog = line  
              lastline = line

          if file_is_empty:
              lastline = {}
              lastline['id'] = -1
          else:
              lastline = json.loads(lastline.rstrip())

          if last_worklog:
              last_worklog = json.loads(last_worklog.rstrip())
          else:
              last_worklog = {}
              last_worklog['total'] = 0


          #Find the new total time
          total = duration.seconds + last_worklog['total'] 
          total_readable = seconds_to_jira_hours(total, False) 

          #Add totaltime and worklog to modified task
          modified['totaltime'] = total_readable 
          if 'worklog' in modified:
              pass
          else:
              modified['worklog'] = 'To see work logs type: "task <TASK-ID> worklog"' 

          #Store this data in worklog.data file
          worklog = {}
          worklog['uuid'] = modified['uuid']
          worklog['start'] = start
          worklog['end'] = end
          worklog['duration'] = duration.seconds
          worklog['readable'] = current_readable
          worklog['total'] = total 
          worklog['id'] = int(lastline['id']) + 1

          if tempo_timesheets_enabled(config):
              log_time = True
              if 'log_tempo' in modified:
                  if modified['log_tempo'] == 'False':
                      log_time = False    
              if log_time:
                  worklog['description'] = tty_input("Enter description for logged time: ")
                  worklog['timesheets'] = tempo_register_time(worklog, modified)

          f.write(DateTimeEncoder().encode(worklog))
          f.write('\n')

          print messages.LOGGED_TIME  % (current_readable, total_readable)
          f.close()
          

  return json.dumps(modified, separators=(',',':')) #Taskwarrior only accepts JSON with no spaces between keys 

def worklog_report(original, modified, config):
  data_path = config['data']['location']
  worklogs = []
  table = None

  with open(os.path.expanduser(data_path + '/worklog.data'), 'r') as f:
      regexp = re.compile(r'\"uuid\": \"%s\"' % modified['uuid'])
      for line in f.readlines():
          if regexp.search(line) is not None:
              worklogs.append(json.loads(line.rstrip()))
      f.close()

  if worklogs:
      if tempo_timesheets_enabled(config):
          table = generate_tempo_table(worklogs)
      else:
          table = generate_table(worklogs)

      table.sortby = "Date"
      table.reversesort = True
      print table
  else:
      print 'No worklogs recorded for this task yet'
  return json.dumps(original, separators=(',',':'))

def generate_table(worklogs):
  table = PrettyTable(['Worklog ID', 'Date', 'Start Time', 'End Time', 'Time Logged', 'Total Time'])

  for worklog in worklogs:
      general = get_general_values(worklog)
      table.add_row([worklog['id'], general['end_date'].date(), general['start_date'].time(), general['end_date'].time(),\
                     general['seconds'], general['total']])

  return table

def generate_tempo_table(worklogs):
  table = PrettyTable(['Worklog ID', 'Date', 'Start Time', 'End Time', 'Description', 'Time Logged', 'Total Time', 'In Tempo?'])

  for worklog in worklogs:
      general = get_general_values(worklog)
      description = None
      in_tempo = ''

      if 'timesheets' in worklog:
          if worklog['timesheets'] == 'True':
              in_tempo = u'\u2713' #Unicode for a check mark

      if 'description' in worklog:
          description = worklog['description'] 
      else:
          description = '' 

      table.add_row([worklog['id'], general['end_date'].date(), general['start_date'].time(), general['end_date'].time(),\
                     description, general['seconds'], general['total'], in_tempo])

  return table

def get_general_values(worklog):
  values = {}
  values['end_date'] = iso8601.parse_date(worklog['end']).replace(microsecond=0)
  values['start_date'] = iso8601.parse_date(worklog['start'])
  values['seconds'] = seconds_to_jira_hours(int(worklog['duration']), False)
  values['total'] = seconds_to_jira_hours(int(worklog['total']), False)

  return values

def tempo_register_time(worklog, modified):
    tempo = TEMPO()
    issue_key = None
    project_match = None
    description_match = None

    if 'project' in modified:
        project_match = find_jira_issue_key(modified['project'])
    if 'description' in modified:
        description_match = find_jira_issue_key(modified['description'])

    if 'jiraid' in modified: 
        issue_key = modified['jiraid']
    elif project_match is not None:
        issue_key = project_match  
        modified['jiraid'] = issue_key
    elif description_match is not None:
        issue_key = description_match
        modified['jiraid'] = issue_key
    else:
        log_in_tempo = query_yes_no('Would you like to tether this task to a JIRA issue to log time against?')
        if log_in_tempo:
            user_key = tty_input('Please provide an issue key to associate with this task: ')
            while find_jira_issue_key(user_key) is None:
                user_key = tty_input('Please provide valid JIRA issue key: ')
            modified['jiraid'] = user_key
            modified['log_tempo'] = 'True'
            issue_key = user_key
        else:
            modified['log_tempo'] = 'False'

    try:
        jira_duration = seconds_to_jira_hours(worklog['duration'])
        tempo.add_worklog(issue_key, jira_duration, worklog['description'], date=worklog['end'].date())
    except TempoError as error:
        regexp = re.compile(r'Remaining estimate is 0h.')
        if 'Remaining estimate is invalid' == error.text or regexp.search(error.text) is not None:
            remaining_estimate = tty_input('Remaining estimate for this issue is invalid, please enter new estimate: ')
            tempo.add_worklog(issue_key, jira_duration, worklog['description'], date=worklog['end'].date(), remaining_estimate = remaining_estimate)
        else:
          print "TEMPO TIMESHEETS ERROR: %s" % error.text 
          return 'False'

    return 'True'

def query_yes_no(question, default='yes'):
    '''Ask a yes/no question via tty_input() and return their answer in boolean.

    "question" is a string that is presented to the user
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    '''

    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        choice = tty_input(question + prompt).lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            tty_output("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

if __name__ == '__main__':
    main(); 
