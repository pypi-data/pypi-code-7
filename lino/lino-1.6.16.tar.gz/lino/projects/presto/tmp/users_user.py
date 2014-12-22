# -*- coding: UTF-8 -*-
logger.info("Loading 4 objects to table users_user...")
# fields: id, modified, created, username, password, profile, initials, first_name, last_name, email, remarks, language, partner, access_class, event_type
loader.save(create_users_user(3,dt(2014,12,20,13,22,31),dt(2014,12,20,13,22,29),u'romain',u'pbkdf2_sha256$12000$9xQPQuhVlpnX$ZNX0uHZl8sEe8pB12VeRNzPgwLeagZP3vIaZy8zNvPs=','900',u'RR',u'Romain',u'Raffault',u'luc.saffre@gmx.net',u'',u'fr',None,u'30',None))
loader.save(create_users_user(2,dt(2014,12,20,13,22,31),dt(2014,12,20,13,22,29),u'rolf',u'pbkdf2_sha256$12000$hPUoXIOb1TB2$A6XKUQmK0DEAHMLgtQgWk1Kh6S6TcV4cOr1kRQLknDc=','900',u'RR',u'Rolf',u'Rompen',u'luc.saffre@gmx.net',u'',u'de',None,u'30',None))
loader.save(create_users_user(1,dt(2014,12,20,13,22,31),dt(2014,12,20,13,22,29),u'robin',u'pbkdf2_sha256$12000$rEYxUE3qgk1M$UUBkqX9vbCs6KlO+0Bb/LpO+LWulx5u04dgOVFwlsAc=','900',u'RR',u'Robin',u'Rood',u'luc.saffre@gmx.net',u'',u'en',None,u'30',None))
loader.save(create_users_user(4,dt(2014,12,20,13,22,31),dt(2014,12,20,13,22,29),u'rando',u'pbkdf2_sha256$12000$fwznRD5wHOWH$XS7urokoy0lYwC9MwZD0+hou+0gcOJs/i/di7Kx6bog=','900',u'RR',u'Rando',u'Roosi',u'luc.saffre@gmx.net',u'',u'et',None,u'30',None))

loader.flush_deferred_objects()
