import requests, logging, re

from django.core.management.base import BaseCommand, CommandError
from time import localtime, time, mktime

import logging
from django.conf import settings


logger = logging.getLogger("thermostat.stats")
logger.setLevel(settings.LOG_LEVEL)


class Command(BaseCommand):
    args = ''
    help = 'Parse de date stats file to retrieve the statistics aggregation for the last N minutes.'

    def _time_range(self, length):
        current = time()
        return [float(current - length * 60), float(current)]

    def handle(self, *args, **options):
#        logging.basicConfig(level=logging.DEBUG)
        
        if len(args) != 1:
            self.stderr.write("Please send argument of how many minutes")
            exit(1)
        with open(settings.FLAME_STATS_PATH) as f:
            contents = f.readlines()
        t_range = self._time_range(int(args[0]))
#        logging.debug("Time range %s" % t_range)
        cont = 0
        
        last_start = None
        data = []
        for line in contents:
            cont = cont + 1
            m = re.search("(\d+\.\d+)\n$", line)
            
            if m is None:
                logging.warn("Format of line %d not correct, cannot find time from epoch at the end" % cont)
                continue
            time = float(m.groups(0)[0])
            
            m = re.search("^(ON|OFF)", line)
            if m is None:
                logging.warn("Format of line %d not correct, cannot find ON|OFF action at the beginning" % cont)
                continue
            action = m.groups(0)[0]
            
            if time < t_range[0] or time > t_range[1]:
                logging.debug("Dejamos la linea %d fuera porque se sale del rango pedido" % cont)
                #initialize the last_start so we know it even if it occur before the time range 
                #if the line is OFF we put last_start = None so the state of the flame is off
                if action == "ON":
                    last_start = time
                else:
                    last_start = None 
                continue
            
            data.append([action, time])
        #print data 
        #print "last_Start: %s " % last_start
        last_heating_period = None
        total_heating_period = 0
        for action, time in data:
            if action == "ON":
                last_start = time
                last_heating_period = None
            if action == "OFF" and last_start is not None:
                #TODO que pasa si last_start es None
                last_heating_period = time - last_start 
                last_start = None
                
            total_heating_period = int(total_heating_period) + int((last_heating_period if last_heating_period is not None else 0))
            """
            logging.debug("action: %s time: %d; %d %d %d" % (
                        action, 
                        time,
                        last_heating_period if last_heating_period is not None else 0,
                        last_start if last_start is not None else 0,
                        total_heating_period))
            """
        #si there is no data (for example: every line was out of time range, we need to know
        #the status of the flame. Therefore we use the last_start, which is set above, when the time range uis checked
        if len(data) == 0 and last_start is not None:
   #         print "como todas las lineas son anteriores al periodo y esta arrancado desde antes, le meto el tiempo desde el principio del periodo"
            total_heating_period = int(args[0]) * 60
   #         print total_heating_period
        #if the first action in data is OFF, means the flame was on by the starting of the time range
        #it is needed to add this time
        if len(data) and data[0][0] == "OFF":
  #          print data[0][1]
    #        print "como la pimera linea es OFF tenemos que add el tiempo desde el principip del periodo hasta el OFF, ates: %s" % total_heating_period
             
            total_heating_period = int(total_heating_period) + int(data[0][1] - t_range[0])
     #       print "despuest %s " % total_heating_period
        
        #if the last action is ON, need to add the time from the instance of that last action,
        #to the end of the range
        if len(data) and data[len(data)-1][0] == "ON":
            total_heating_period = int(total_heating_period) + int(t_range[1] - data[0][1])
        
        try:
            total_seconds = int(args[0]) * 60
            print("absolute:%d percent:%.2f" % (total_heating_period, (100 * total_heating_period ) / total_seconds))
        except Exception as er:
            logger.error("Exception while trying to return the value: %s " % er)
            
