# Authors: Pablo Saavedra
# Contact: saavedra.pablo@gmail.com

"""
This package contains DAO implementation fro SQLite3 module.
"""


from pyncomings import dao

import sqlite3




class DAOEntry(dao.DAOEntry):
    """
    entry = {
         "registration_date": None,
         "source": None,
         "size": None,
         "path": None,
         "user": None,
         "retention_days": None,
         "purged_date": None,
        }

    """

    def __init__(self, sqlite3_filename):
        self.conn = sqlite3.connect(sqlite3_filename,
                detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)


    def create_table(self):
        c = self.conn.cursor()
        c.execute('''create table entries 
        (registration_date text, 
         source text, size text,
         path text primary key, user text,
         retention_days real, 
         purged_date text
        )''')
        
        self.conn.commit()
        c.close()

    def create_entry(self, entry):
        
        c = self.conn.cursor()
        c.execute('''insert into entries (registration_date, source, size,
        path, user, retention_days, purged_date) values
        (?, ?, ?, ?, ?, ?, ?)''' ,
                (entry['registration_date'], entry['source'], entry['size'],
                 entry['path'], entry['user'],
                 entry['retention_days'],entry['purged_date']
                ))
        
        self.conn.commit()
        c.close()

    def get_entry(self, path):
        c = self.conn.cursor()
        query = '''select registration_date, source, size, path, user,
        retention_days, purged_date from entries where path="%s"''' % path
        c.execute(query)
        r = c.fetchone()
        c.close()

        if r:
          res = {
           "registration_date": r[0],
           "source": r[1],
           "size": r[2],
           "path": r[3],
           "user": r[4],
           "retention_days": r[5],
           "purged_date": r[6],
          }
        else:
            res = None

        return res

    def get_entries(self, offset=None, max_items=None):
        res = []
        c = self.conn.cursor()
        if not offset:
          if not max_items:
            for r in c.execute('''select registration_date, 
            source, size, path, user, retention_days, purged_date from entries'''):
              item = {
                      "registration_date": r[0],
                      "source": r[1],
                      "size": r[2],
                      "path": r[3],
                      "user": r[4],
                      "retention_days": r[5],
                      "purged_date": r[6],
                     }
              res.append(item)
        else:
          raise NotImplementedError

        c.close()
        return res


    def update_entry(self, entry):
        c = self.conn.cursor()
        
        c.execute('''update entries set registration_date=?, source=?,
        size=?,
        user=?, retention_days=?, purged_date=?
        where path=?''',
                (entry['registration_date'], entry['source'], entry['size'],
                 entry['user'],
                 entry['retention_days'],entry['purged_date'],
                 entry['path']
                ))
        
        self.conn.commit()
        c.close()


    def delete_entry(self, path):
        c = self.conn.cursor()
        c.execute('''delete from entries where path="%s"''' % path)
        self.conn.commit()
        c.close()


    def search_entry_by_date(self, date):
        res = []
        c = self.conn.cursor()
        
        for r in c.execute('''select registration_date, 
            source, size, path, user, retention_days, purged_date from entries
            where path like "%s"''' % date):
    
              item = {
                      "registration_date": r[0],
                      "source": r[1],
                      "size": r[2],
                      "path": r[3],
                      "user": r[4],
                      "retention_days": r[5],
                      "purged_date": r[6],
                     }
              res.append(item)

        c.close()
        return res




def test():

  e1 = {
         "registration_date": "e1",
         "source": "e1",
         "size": "e1",
         "path": "e1",
         "user": "e1",
         "retention_days": 1,
         "purged_date": "e1",
        }


  e2 = {
         "registration_date": "e2",
         "source": "e2",
         "size": "e2",
         "path": "e2",
         "user": "e2",
         "retention_days": 2,
         "purged_date": "e2",
        }

  d = DAOEntry(":memory:")
  d.create_table()

  
  print "Get_entry result e1: " + str(d.get_entry(e1["path"]))

  d.update_entry(e1)
  ee = d.get_entries()
  print "Entries: " + str(ee)


  d.create_entry(e1)
  try:
    d.create_entry(e1)
    print "Error, can enter a entry with a path entry previously."
  except sqlite3.IntegrityError:
    print "OK: Integrity error success"
    

  d.create_entry(e2)

  ee = d.get_entries()
  print "Entries: " + str(ee)

  print "Entry e1: " + str(e1)
  print "Get_entry result e1: " + str(d.get_entry(e1["path"]))
  print "Entry e2: " + str(e2)
  print "Get_entry result e2: " + str(d.get_entry(e2["path"]))
  
  ee = d.search_entry_by_date(e1["registration_date"])
  print "Result for e1['registration_date'] search: " + str(ee)

  e22 = e2
  e22["size"]="SIZE22"
  d.update_entry(e22)
  
  ee = d.get_entry(e22["path"])
  print "Query result e2 (size modified): " + str(ee)
  
  d.delete_entry(e1["path"])
  ee = d.get_entry(e1["path"])
  print "Query result e1 (after deletion): " + str(ee)


if __name__ == '__main__':
    test()
