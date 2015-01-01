import mrrapi

mkey = ''
msecret = ''
demo = mrrapi.api(mkey,msecret)

print "List Scrypt rigs over 10 MH"
rigs = demo.rig_list(min_hash=10, max_cost=0.00075)
arigs = rigs['data']['records']

print rigs['data']['info']['available']['rigs'] + "\t Total Rigs available for rent."
print rigs['data']['info']['rented']['rigs'] + "\t Rigs Rented"
print str(len(arigs)) + "\t Available with your specs."

print rigs['data']

for x in arigs:
    print x
