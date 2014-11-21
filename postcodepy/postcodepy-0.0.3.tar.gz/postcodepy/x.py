
def getit( pc, nr, ad=""):
  print "PC: ", pc
  print "NR: ", nr
  print "AD: ", ad


for PC in [ ('8422DH', 34), ('8422DH', 34, 'A') ] :
  getit(  unpack(PC  ))
