#/usr/bin/python
'''this is a eg. for how to use for if else and isinstance function'''
li=["a","b",["cc","dd"],["e",["ff","gg"]]]
#for i in li:
#  if isinstance(i,list):
#     for o in i:
#       if isinstance(o,list):
#           for w in o:
#              print w 
#       else:    
#           print o
#  else:
#     print i




def kkk(li):
  for mm in li:
     if isinstance(mm,list):
         kkk(mm)
     else: 
         print mm
kkk(li)
