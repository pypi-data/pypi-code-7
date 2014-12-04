import signal
import os
import sys
import json
import datetime
import base64
import socket
from tup import *

class UserEndCycleException(Exception):
  pass

class ParentDeadException(Exception):
  pass

class Controller:

  READ_SOFT_TIMEOUT = 20 # Amount of time to wait until we send a 'ping' to the parent
  DEATH_TIMEOUT = READ_SOFT_TIMEOUT * 3  # If no activity from the parent (even response to a ping) time before we kill ourself.

  def __init__(self, emits, options = {}):
    
    self.last_activity = None
    self.emits = emits
    host = options.get("host", None)
    port = options.get("port", None)
    unix_socket = options.get("unix_socket", None)
    
    if(host != None and port != None):
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.connect((host, int(port)))
      self.socket_to_java = sock.makefile('r+w', 1)
      self.socket_from_java = self.socket_to_java
    elif(unix_socket != None):
      sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
      sock.connect(unix_socket)
      self.socket_to_java = sock.makefile('r+w', 1)
      self.socket_from_java = self.socket_to_java
    else:
      self.socket_to_java = sys.stdout
      self.socket_from_java = sys.stdin

  def pjson(self, m):
    jd = json.dumps(m)
    self.socket_to_java.write(jd+"\n")
    self.socket_to_java.write("end\n")
    self.socket_to_java.flush()

  def emit(self, *args):
    # convert tuple to json, print to stdout
    m = {"command":"emit"}
    m["stream"] = None
    m["tuple"] = {}

    if(len(args) == 1):
      m["tuple"] = args[0]
    elif(len(args) == 2):
      if isinstance(args[0], basestring):
        m["stream"] = args[0]
        m["tuple"] = args[1]
      elif isinstance(args[0], dict):
        m["tuple"] = args[0]
    elif(len(args) == 3):
      m["stream"] = args[0]
      m["tuple"] = args[1]

    if isinstance(m["tuple"], Tuple):
      m["tuple"] = m["tuple"].values

    if(m["stream"] == None):
      m["stream"] = self.emits[0]

    self.pjson(m)

  def log(self, message):
    # convert to json, print to stdout
    m = {"command":"log"}
    m["msg"] = message
    self.pjson(m)

  def ack(self, idn):
    if idn == None:
      self.log("Invalid id")
    else:
      m = {"command":"ack", "id":idn}
      self.pjson(m)

  def fail(self, message):
    if message == None:
      self.log("no error message")
    else:
      m = {"command":"fail", "msg":message}
      self.pjson(m)

  def done(self):
    m = {"command":"done"}
    self.pjson(m)

  def end_cycle(self):
    m = {"command":"end_cycle"}
    self.pjson(m)
    raise UserEndCycleException("cycle ended")

  def check_end(self):
    line = self.socket_from_java.readline()
    while line != "end\n":
      self.log("Missing end checking next line")
      line = self.socket_from_java.readline()
    return True

  def read(self):
    def timed_read(c, m):
      try:
        line = c.socket_from_java.readline()
        try:
          d = json.loads(line)
          m["msg"] = d
        except:
          c.log("Cannot be parsed to JSON " + line)
          m["msg"] = None
        c.check_end()
        c.last_activity = datetime.datetime.now()
      except KeyboardInterrupt:
        raise
      except: # This happens on time-out (set below)
        if c.last_activity + datetime.timedelta(0,Controller.DEATH_TIMEOUT) < datetime.datetime.now():
          raise ParentDeadException("jvm appears to be dead")
        else:
          c.pjson({"ping":(datetime.datetime.utcnow()-datetime.datetime(1970,1,1)).total_seconds()})
        msg_from_java["msg"] = None

    if self.last_activity == None:
      self.last_activity = datetime.datetime.now()

    signal.signal(signal.SIGALRM, timed_read)
    signal.alarm(Controller.READ_SOFT_TIMEOUT)

    msg_from_java = {}
    timed_read(self, msg_from_java)

    if msg_from_java["msg"] != None and "pong" in msg_from_java["msg"]: # ignore pongs
      msg_from_java["msg"] = None

    return msg_from_java["msg"]

  def get_tuple(self, d):
    try:
      tup = d["tuple"]
    except:
      self.log("Missing tuple field in emitted JSON object")
      return None
    full_tuple = Tuple(d)
    return full_tuple

  def get_tuples(self, d):
    try:
      tup = d["tuples"]
    except:
      self.log("Missing tuple field in emitted JSON object")
      return None
    tuples = map(lambda t : Tuple(t), d["tuples"])
    return tuples

  def get_pidDir(self):
    d = self.read()
    cmd = d["pidDir"]
    m = {}
    m["pid"] = os.getpid()
    self.pjson(m)
