
import kadmin_local as kadmin

k = kadmin.local({'host':'ldapi:///'})

for p in k.principals('aa*'):
    print p


