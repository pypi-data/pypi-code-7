import mrrapi
import mrrapi.helpers

(mkey, msecret) = mrrapi.helpers.getmrrconfig()
mapi = mrrapi.api(mkey,msecret)


ra = mapi.rig_listall(min_hash=30)
print "RA="
print ra
