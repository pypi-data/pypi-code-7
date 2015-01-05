import json
import os
import sys
import datetime
import messages

def has_totaltime_uda(config):
    if 'uda' in config:
      if 'totaltime' in config['uda']:
        if ('type' in config['uda']['totaltime']) and ('label' in config['uda']['totaltime']):
          return True 
    print messages.TIMELOG_NOT_IN_CONFIG
    return False

def has_worklog_uda(config):
    if 'uda' in config:
      if 'worklog' in config['uda']:
        if 'type' in config['uda']['worklog'] and 'label' in config['uda']['worklog']:
          return True
    print messages.WORKLOG_NOT_IN_CONFIG
    return False

def tempo_timesheets_enabled(config):
    if 'timesheets' in config:
      if 'jira' in config['timesheets']:
        if (config['timesheets']['jira'] == 'True'):
          return True
    else:
      return False 

def tty_input(prompt):
    #Make copies of stdout and stdin
    old_stdout = sys.stdout
    old_stdin = sys.stdin
    #Open tty which is a system file object that represents the current console,
    #then route stdin and stdout to it and get input 
    tty = open('/dev/tty')
    sys.stdin = tty
    sys.stdout = tty
    user_input = raw_input(prompt)
    #Restore stdin and stdout to what it used to be
    sys.stdout = old_stdout
    sys.stdin = old_stdin

    return user_input

def tty_output(message):
    old_stdout = sys.stdout
    tty = open('/dev/tty')
    sys.stdout = tty

    sys.stdout.write(message)

    sys.stdout = old_stdout

def seconds_to_jira_hours(seconds, jira=True):
    if not isinstance(seconds, (int, float)):
        raise TypeError('Expected int/float but got %s' % type(seconds))

    if (jira):
        units = [
            ('s', 1),
            ('m', 60),
            ('h', 3600),
            ('d', 86400),
        ]
    else:
        units = [
            ('seconds', 1),
            ('minutes', 60),
            ('hours', 3600),
            ('days', 86400),
        ]

    def _iter(seconds_left):
        if units:
            unit, value = units.pop()
            if seconds_left < value:
                return _iter(seconds_left)
            if (jira):
                return ('%s%s %s' % (seconds_left / value, unit,
                                     _iter(seconds_left % value)))
            else:
                return ('%s %s %s' % (seconds_left / value, unit,
                                     _iter(seconds_left % value)))

        return ''

    return _iter(seconds).strip() or '0h'

def ceil_datetime(dt, seconds):
    nsecs = dt.minute*60+dt.second+dt.microsecond*1e-6  
    #number of seconds to next quarter hour mark
    #Non-analytic (brute force is fun) way:  
    #   delta = next(x for x in xrange(0,3601,900) if x>=nsecs) - nsecs
    #anlytic (ARGV BATMAN!, what is going on with that expression) way:
    delta = (nsecs//seconds)*seconds+seconds-nsecs
    #time + number of seconds to quarter hour mark.
    return dt + datetime.timedelta(seconds=delta)

def round_time(dt, roundTo):
    """Round a datetime object to any time laps in seconds
    dt : datetime.datetime object, default now.
    roundTo : Closest number of seconds to round to, default 1 minute.
    Author: Thierry Husson 2012 - Use it as you want but don't blame me.
    """
    dt = dt.replace(tzinfo=None) #Get rid of timezone awareness
    seconds = (dt - dt.min).seconds
    rounding = (seconds+roundTo/2) // roundTo * roundTo
    return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)

def date_handler(obj):
  if hasattr(obj, 'isoformat'):
    return obj.isoformat()
  elif isinstance(obj, datetime.datetime):
    return obj.isoformat()
  elif isinstance(obj, datetime.date):
    return obj.isoformat()
  elif isinstance(obj, datetime.timedelta):
    return obj.isoformat()
  else:
    raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))

class DateTimeEncoder(json.JSONEncoder):
  def default(self, obj):
      if isinstance(obj, datetime.datetime):
          return obj.isoformat()
      elif isinstance(obj, datetime.date):
          return obj.isoformat()
      elif isinstance(obj, datetime.timedelta):
          return (datetime.datetime.min + obj).time().isoformat()
      else:
          return super(DateTimeEncoder, self).default(obj)

def load_config(config_filename="~/.taskrc"):
    """ Taken from https://github.com/ralphbean/taskw and fixed to allow
    a key to have multiple children

    Load ~/.taskrc into a python dict

    >>> config = TaskWarrior.load_config()
    >>> config['data']['location']
    '/home/threebean/.task'
    >>> config['_forcecolor']
    'yes'

    """

    with open(os.path.expanduser(config_filename), 'r') as f:
        lines = f.readlines()

    _usable = lambda l: not(l.startswith('#') or l.strip() == '')
    lines = filter(_usable, lines)

    def _build_config(pieces, value, d):
        """ Called recursively to split up keys """
        if len(pieces) == 1:
            d[pieces[0]] = value.strip()
        else:
            if (pieces[0] not in d):
              d[pieces[0]] = {}
            _build_config(pieces[1:], value, d[pieces[0]]) 

    d = {}
    for line in lines:
        if '=' not in line:
            continue

        key, value = line.split('=', 1)
        pieces = key.split('.')
        _build_config(pieces, value, d)

    # Set a default data location if one is not specified.
    if d.get('data') is None:
        d['data'] = {}

    if d['data'].get('location') is None:
        d['data']['location'] = os.path.expanduser("~/.task/")

    return d

