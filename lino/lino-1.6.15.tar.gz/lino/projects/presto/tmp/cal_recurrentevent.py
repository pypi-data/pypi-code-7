# -*- coding: UTF-8 -*-
logger.info("Loading 9 objects to table cal_recurrentevent...")
# fields: id, user, name, start_date, start_time, end_date, end_time, every_unit, every, monday, tuesday, wednesday, thursday, friday, saturday, sunday, max_events, event_type, description
loader.save(create_cal_recurrentevent(1,None,[u"New Year's Day", u'Neujahr', u"Jour de l'an", u'Uusaasta'],date(2013,1,1),None,None,None,u'Y',1,True,True,True,True,True,True,True,None,1,u''))
loader.save(create_cal_recurrentevent(2,None,[u"International Workers' Day", u'Tag der Arbeit', u'Premier Mai', u'kevadp\xfcha'],date(2013,5,1),None,None,None,u'Y',1,True,True,True,True,True,True,True,None,1,u''))
loader.save(create_cal_recurrentevent(3,None,[u'National Day', u'Nationalfeiertag', u'F\xeate nationale', u'Belgia riigip\xfcha'],date(2013,7,21),None,None,None,u'Y',1,True,True,True,True,True,True,True,None,1,u''))
loader.save(create_cal_recurrentevent(4,None,[u'Assumption of Mary', u'Mari\xe4 Himmelfahrt', u'Assomption de Marie', u'Assumption of Mary'],date(2013,8,15),None,None,None,u'Y',1,True,True,True,True,True,True,True,None,1,u''))
loader.save(create_cal_recurrentevent(5,None,[u"All Souls' Day", u'Allerseelen', u'Comm\xe9moration des fid\xe8les d\xe9funts', u"All Souls' Day"],date(2013,10,31),None,None,None,u'Y',1,True,True,True,True,True,True,True,None,1,u''))
loader.save(create_cal_recurrentevent(6,None,[u"All Saints' Day", u'Allerheiligen', u'Toussaint', u"All Saints' Day"],date(2013,11,1),None,None,None,u'Y',1,True,True,True,True,True,True,True,None,1,u''))
loader.save(create_cal_recurrentevent(7,None,[u'Armistice with Germany', u'Waffenstillstand', u'Armistice', u'Armistice with Germany'],date(2013,11,11),None,None,None,u'Y',1,True,True,True,True,True,True,True,None,1,u''))
loader.save(create_cal_recurrentevent(8,None,[u'Christmas', u'Weihnachten', u'No\xebl', u'Esimene J\xf5ulup\xfcha'],date(2013,12,25),None,None,None,u'Y',1,True,True,True,True,True,True,True,None,1,u''))
loader.save(create_cal_recurrentevent(9,None,[u'Summer holidays', u'Sommerferien', u"Vacances d'\xe9t\xe9", u'Suvevaheaeg'],date(2013,7,1),None,date(2013,8,31),None,u'Y',1,True,True,True,True,True,True,True,None,1,u''))

loader.flush_deferred_objects()
