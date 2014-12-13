
import os
import sys
import radical.pilot as rp

def pilot_state_cb (pilot, state) :

    print "[Callback]: ComputePilot '%s' state: %s." % (pilot.uid, state)
    if  state == rp.FAILED:
        sys.exit (1)

def unit_state_cb (unit, state) :

    print "[Callback]: ComputeUnit  '%s' state: %s." % (unit.uid, state)

    if state in [rp.FAILED] :
        print "stdout: %s" % unit.stdout
        print "stderr: %s" % unit.stderr


os.system ('date     > file0.dat')
os.system ('hostname > file1.dat')
os.system ('date     > file2.dat')
os.system ('hostname > file3.dat')
os.system ('date     > file4.dat')
os.system ('hostname > file5.dat')
os.system ('date     > file6.dat')
os.system ('hostname > file7.dat')
os.system ('date     > file8.dat')
os.system ('hostname > file9.dat')

s = rp.Session()

pmgr = rp.PilotManager (s)
umgr = rp.UnitManager  (s, scheduler=rp.SCHED_ROUND_ROBIN)

pmgr.register_callback(pilot_state_cb)
umgr.register_callback(unit_state_cb)

pdesc = rp.ComputePilotDescription()
pdesc.resource  = "local.localhost"
pdesc.runtime   = 15 # minutes
pdesc.cores     = 1

umgr.add_pilots(pmgr.submit_pilots(pdesc))

cuds = list()

for i in range (1) :
    cud = rp.ComputeUnitDescription()
    cud.executable    = "/bin/date"
    cud.input_staging = list()
    for f in  ['file1.dat', 'file2.dat',
               'file3.dat', 'file4.dat',
               'file5.dat', 'file6.dat',
               'file7.dat', 'file8.dat',
               'file9.dat', 'file0.dat'] :
        cud.input_staging.append ({
            'source' : f, 
            'target' : "t/%s" % f, 
            'flags'  : rp.CREATE_PARENTS})

    cuds.append(cud)

units = umgr.submit_units(cuds)

umgr.wait_units()

s.close()

os.system ('rm file0.dat')
os.system ('rm file1.dat')
os.system ('rm file2.dat')
os.system ('rm file3.dat')
os.system ('rm file4.dat')
os.system ('rm file5.dat')
os.system ('rm file6.dat')
os.system ('rm file7.dat')
os.system ('rm file8.dat')
os.system ('rm file9.dat')

