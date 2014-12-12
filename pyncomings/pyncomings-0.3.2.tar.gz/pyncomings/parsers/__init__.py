# Authors: Pablo Saavedra
# Contact: saavedra.pablo@gmail.com

"""
This package contains Pycomings Parsers modules.
"""

import time

class LogFileParser(object):

    """
    Base class for pycomings LogFileParsers.

    Each writer module or package must export a subclass also called
    'LogFileParsers'.

    The `send()` method is the main entry point.
    """

    mark_file=""
    jobs=[]
    stop=False

    def __init__(self, mark_file, jobs=[]):
        self.mark_file = mark_file
        self.jobs = jobs

    def parse_line(self, line):
        """
        Parse a log line.

        Normally overridden or extended in subclasses.
        """
        raise NotImplementedError

    def parse_lines(self, lines):
        """
        Parse a list of lines.

        Normally overridden or extended in subclasses.
        """
        raise NotImplementedError


    def save_mark(self,line):
      """ This function saves de last processed line """

      try:
        f = open(self.mark_file, 'w')
        f.write(line)
        f.close()
      except Exception,e:
        print e

    def load_mark(self):
      """ This function load de last processed line """

      try:
        f = open(self.mark_file)
        line = f.readline()
        f.close()
        return line
      except Exception,e:
        f = open(self.mark_file, 'w')
        f.close()
        print e
        return ""

      
    def watch_logs(self, logfile_names,sleeping_success,sleeping_no_incoming_lines):
        """
        While not "stop" value is active, then this method wacth the
        logfiles.
        """
        
        f,buffer_ = get_pending_lines(logfile_names)
        while not self.stop:
          if not len(buffer_) == 0:
           time.sleep(sleeping_no_incoming_lines)
           f,buffer_ = get_pending_lines(logfile_names)
          else:
           for l in buffer_:
               for j in self.jobs:
                   # Executed job for this line
                   j(l)
           self.save_mark(l)
           time.sleep(sleeping_success)
           buffer_ = f.readlines()


    def get_pending_lines(self, logfile_names):
        """
        Search pending lines to proccess. This function read lines for the 
        log file. then:

        - Search proccessed mark into the buffer:
 
          * if mark dont exist, return ''buffer''
          * if mark exist:

            * if mark is into main log file:
              buffer = buffer - previously processed lines.      
            * if it is founded into rotated log tipically (*.1):
              buffer = log rotated pending lines + buffer
            * if it is not founded into any logfile:
              buffer = log rotated lines + buffer
        
        Return: ( logfile[0] open, pending lines list)
        """

        f = open(logfile_names[0])
        buffer_ = f.readlines()

        mark =  self.load_mark()
        if not mark:
          print "Mark not founded"
          return (f,buffer_)

        # (else)
        try:
          # check if mark exist into buffer ...
          buffer_.index(mark)
          # ... this method can raise ValueError exception

          buffer_ = buffer_[buffer_.index(mark)+1:]
          # print "Mark founded into primarly log file"
          return (f,buffer_)

        except ValueError, e:

          # mark dont founded into buffer ...
          try:
            rotated_file=open(logfile_names[1])
            rotated_buffer=rotated_file.readlines()
  
            try:
              rotated_buffer.index(mark)
              buffer_ = \
                rotated_buffer[rotated_buffer.index(mark)+1:] \
                + buffer_
              # print "Mark founded into secondary log file"
              return (f,buffer_)
            except ValueError, e:
              # mark dont founded into rotated_buffer
              buffer_ = rotated_buffer + buffer_
              # print "Mark dont founded into primarly and secondary log file"
              return (f,buffer_)

          except Exception, e:
            # print "Can not open rotated log file."
            return (f,buffer_)

        raise Exception()
