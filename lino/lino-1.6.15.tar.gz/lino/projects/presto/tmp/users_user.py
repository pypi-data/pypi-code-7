# -*- coding: UTF-8 -*-
logger.info("Loading 4 objects to table users_user...")
# fields: id, modified, created, username, password, profile, initials, first_name, last_name, email, remarks, language, partner, access_class, event_type
loader.save(create_users_user(3,dt(2014,12,12,5,37,23),dt(2014,12,12,5,37,21),u'romain',u'pbkdf2_sha256$12000$vBsHHz2kehhp$YewE9CL3MVDpeBWq/XrS7tZrOrX/0tNhfcBMb9K+Gu8=','900',u'RR',u'Romain',u'Raffault',u'luc.saffre@gmx.net',u'',u'fr',None,u'30',None))
loader.save(create_users_user(2,dt(2014,12,12,5,37,23),dt(2014,12,12,5,37,21),u'rolf',u'pbkdf2_sha256$12000$gKqQaWnG0mei$nbEnfNPibMTNof9wSnl6j1jXgTCM/7yp6CRqY9zhNSs=','900',u'RR',u'Rolf',u'Rompen',u'luc.saffre@gmx.net',u'',u'de',None,u'30',None))
loader.save(create_users_user(1,dt(2014,12,12,5,37,23),dt(2014,12,12,5,37,21),u'robin',u'pbkdf2_sha256$12000$jvlLmWiTyGjo$B9bxUKVIAE6+8BXiiA7l0cm2PUsbfh20M8Mn+IiwNzM=','900',u'RR',u'Robin',u'Rood',u'luc.saffre@gmx.net',u'',u'en',None,u'30',None))
loader.save(create_users_user(4,dt(2014,12,12,5,37,23),dt(2014,12,12,5,37,21),u'rando',u'pbkdf2_sha256$12000$srY7De4SoxfB$t48D9ttjzrcIxGbdKKdl4LuDPls3bDTAyNi/lQ+OUSg=','900',u'RR',u'Rando',u'Roosi',u'luc.saffre@gmx.net',u'',u'et',None,u'30',None))

loader.flush_deferred_objects()
