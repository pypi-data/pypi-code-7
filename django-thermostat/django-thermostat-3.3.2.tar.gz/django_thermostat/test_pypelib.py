
import requests
import simplejson
from pypelib.RuleTable import RuleTable
from pypelib.Condition import Condition
from pypelib.Rule import Rule
#from pypelib.parsing.drivers import RegexParser
#from pypelib.persistence.backends import rawfile, django
from time import *
from pypelibgui.mappings import get_mappings
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def get_temp(metaObj):
    return requests.get("http://raspberry:8000/rest/temperature").json()["temperature"]
    #return 18


def write_result(meta):
    print "Hemos terminado"


def get_hora(meta):
    return "%f" % mktime(localtime())


def gen_comparing_time(hour, minute, second):
    return mktime(strptime("%s %s %s %d:%d:%d" %(
        strftime("%d", localtime()),
        strftime("%m", localtime()),
        strftime("%Y", localtime()),
        hour,
        minute,
        second), "%d %m %Y %H:%M:%S"))


mappings = get_mappings()


print mappings
print "la hora es: %s" % mktime(localtime())

table = RuleTable(
    "Calecfaccion Invierno laborables",
    mappings,
    "RegexParser",
    #rawfile,
    "RAWFile",
    None)

start_time = gen_comparing_time(19, 00, 00)
print "estar time: %s" % start_time
end_time = gen_comparing_time(22, 00, 00)

print "end time: %s " % end_time
print "current day of week: %s" % mappings["current_day_of_week"]()
print "current temp %s" % mappings["current_temperature"]()
table.setPolicy(False)
#table.addRule("if (current_day_of_week != Sat ) && ( current_day_of_week != Sun) then accept ")
table.addRule("if ((current_day_of_week != Sat ) && ( current_day_of_week != Sun)) && ((current_hour > %f) && (current_hour < %f)) && (current_temperature < confort_temperature) then accept" % (start_time, end_time))
table.addRule("if current_temperature < economic_temperature then accept")



#table.addRule(Rule(Condition("vm.memory","2000",">"),"Memory", "Action forbbiden: You requested more that 2GB of RAM" ,Rule.NEGATIVE_TERMINAL))
#table.addRule(Rule(Condition("project.vms","4",">="),"VMs","Action forbidden: you have 4 VMs already in the project",Rule.NEGATIVE_TERMINAL))
#table.addRule(Rstrptime("30 Nov 00", "%d %b %y")rint ule(Condition("projec t.string","try","!="),"String","Action forbidden: String",Rule.NEGATIVE_TERMINAL))
print "DUMP *******************************"
table.dump()

print "END DUMP *******************************"
#table.save(fileName="rules.txt")

metaObj = {}

#Create the metaObj

try:
    print "evaluamos"
    print "Evaluacion: %s " % table.evaluate(metaObj)
    print "aleluya"
except Exception as e:
    print "Esception: %s" % e
