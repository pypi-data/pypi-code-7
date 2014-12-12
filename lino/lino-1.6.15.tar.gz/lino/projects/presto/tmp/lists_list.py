# -*- coding: UTF-8 -*-
logger.info("Loading 8 objects to table lists_list...")
# fields: id, name, ref, list_type, remarks
loader.save(create_lists_list(1,[u'Announcements', u'Announcements', u'Announcements', u'Kuulutused'],None,1,u''))
loader.save(create_lists_list(2,[u'Weekly newsletter', u'Weekly newsletter', u'Weekly newsletter', u'N\xe4daline infokiri'],None,1,u''))
loader.save(create_lists_list(3,[u'General discussion', u'General discussion', u'General discussion', u'\xdcldine arutelu'],None,2,u''))
loader.save(create_lists_list(4,[u'Beginners forum', u'Beginners forum', u'Beginners forum', u'Algajate foorum'],None,2,u''))
loader.save(create_lists_list(5,[u'Developers forum', u'Developers forum', u'Developers forum', u'Developers forum'],None,2,u''))
loader.save(create_lists_list(6,[u'PyCon 2014', u'PyCon 2014', u'PyCon 2014', u'PyCon 2014'],None,3,u''))
loader.save(create_lists_list(7,[u'Free Software Day 2014', u'Free Software Day 2014', u'Free Software Day 2014', u'Free Software Day 2014'],None,3,u''))
loader.save(create_lists_list(8,[u'Schools', u'Schulen', u'Schools', u'Koolid'],None,3,u''))

loader.flush_deferred_objects()
