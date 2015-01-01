# -*- coding: utf-8 -*-
import mrrapi

demo = mrrapi.api('','')

#print "Rig Detail 6899"
#print demo.rig_detail(7280)
#print "List Scrypt rigs over 10 MH"
#a= demo.rig_list(10,0,0,0,order='price',orderdir='desc')
#print a['data']['records']
#print "List X11 rigs"
#print demo.rig_list(0,0,0,0,'x11')
#print "Get my rigs"
#print demo.myrigs()

#print demo.rig_update(6899,rigName='bob bub',hashrate=57.2,rigStatus='DiSabled')
c = 2**1024
d = 98 * 10**6
e = c/d

print demo.getbalance()

#print demo.rental_detail('123110')
#3055 sha, 700 scrypt

#a = demo.list_profiles()
#print a
#for x in a['data']:
#    print x['name']
#    print x
a = demo.rig_list(0,0,0,0.000000014,"sha256")
print a

#b = demo.rent_rig(700,3,12259)
#print b
