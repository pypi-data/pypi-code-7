"""
This module is based in:

 - Database access modeule (use DAO)
 - Sanitize action (use DAO)
 - Garbage action (use DAO)
 - Pending lines proccess acction
   
   - For each pening line, execute all configured jobs.
   - Record entry into database
   - All problems are explicited in stdout.

 - This module is directly used by executables in tools directory
         
         
Tools:

 - Herramienta que de le dice los ficheros que tiene que parsear y te
   devuelve las lineas no parseadas desde la ultima ejecucion

 - Procesador de medios:
     - Se falicita un ejemplo en el de tarea de cron con fichero de bloqueo
     - Lee de un fichero de configuracion: jobs, directorios y tipo de dao a
       base de datos.
     - Por cada entrada ejecuta tareas 
     - Logea en syslog
     - jobs:

        * 
        * cp del medio a directorio temporal
        * ...

  - Tool de saneamiento: 
     - Modo forzado  o no
     - El modo forzado elimina las entradas de medios que no estan en
       el directorio
     - Revisa los medios no dados de alta
     - Revisa medios dados de alta que no existen

  - Tool de garbage

     - Limpia medios obsoletos 
     - Fichero de configuracion: base de datos, directorio?, tiempo de
       retencion


Test units

 - para los parsers
 - para los dao
 - para la fachada

"""

import pyncomings
# import pyncomings.dao
# import pyncomings.parsers
import os
import time
import re

class PyncomingsManager (object):
  import ConfigParser

  _dao={}
  _parser=None
  logfile_names=[]
  jobs=[]
  retention_days=1095

  def __init__(self,configuration_file):

    # RawConfigParser not interpolate attribute values
     cfg = self.ConfigParser.RawConfigParser()
     cfg.readfp(file(configuration_file))

     # Initialize Global options
     self.retention_days = cfg.get('global','retention_days')
 
     # Initialize database DAO
     database_type = cfg.get('database','type')
     database_file = cfg.get('database','file')
     
     # Adding DAO objects to dao dict ...
     # eval ("import %s" % database_type)
     __import__ (database_type)
     self._dao["DAOEntry"] = eval ("%s.DAOEntry('%s')" \
            % (database_type, database_file))

     # Initialize parser
     self.logfile_names.append(cfg.get('parser','log_name'))
     self.logfile_names.append(cfg.get('parser','rotate_log_name'))
     
     parser_type = cfg.get('parser','type')
     parser_mark_file_name = cfg.get('parser','mark_file_name')

     __import__ (parser_type)
     self._parser = eval ("%s.LogFileParser('%s')"
             % (parser_type, parser_mark_file_name))

     # Initialize jobs
     jobs_id = eval (cfg.get('jobs','ids')) # For example: 'job_1','
     for job_id in jobs_id:
       job_config_file=eval(cfg.get(job_id,'execute'))
       self.jobs.append (job_config_file)
    
  def sanitize_database(self,force_delete=False):
    entries = self._dao["DAOEntry"].get_entries()
    for e in entries:
      if float(e["purged_date"]) == float(0):
        try:
          file(e["path"])
        except IOError:
          # Dont file dont exist
          print "Purging %s" % e["path"]
          e["purged_date"] = time.time()
          self._dao["DAOEntry"].update_entry(e)

  def purge_garbage(self):
    entries = self._dao["DAOEntry"].get_entries()
    for e in entries:
      if float(e["purged_date"]) == float(0):
          limit_date = time.time() - (float (self.retention_days) * 86400)

          if float(e["registration_date"]) < float(limit_date):
            try:
               print "Purging %s" % e["path"]
               e["path"] = self._fix_path(e["path"], True)
               try:
                 os.remove(e["path"])
               except OSError, ex:
                 print ex

               e["purged_date"] = time.time()
               self._dao["DAOEntry"].update_entry(e)

            except Exception, ex:
               print ex


  def clean_purged(self):

    entries = self._dao["DAOEntry"].get_entries()
    for e in entries:
      # If is a entry already purged ...
      if not float(e["purged_date"]) == float(0):

          self._dao["DAOEntry"].delete_entry(e["path"])
          print "Cleaning %s purged file" % e["path"]

  def _fix_path (self,path,noescape=False):

           #XXX: Miramos que entry es un fichero valido en el sistema
           #XXX: Si no lo es, lo buscamos y devolvemos el path real en el
           #     sistema.
           # Cogemos la entrada del log -> le quitamos espacion y barras
           # bajas
           # Cogemos todos los del directorio -> les quitamos los espacios
           # y las barras
           # Los comparamos
           # Cuando machea uno, sabemos que es ESE. Cogemos una parte
           # y construimos el path completo
           if not os.path.exists(path):
               basedir_path = os.path.dirname(path)
               basename_path = os.path.basename(path)
               basename_escaped_path = basename_path.replace(" ","").replace("_","")
               try:
                 all_entries_paths = os.listdir(basedir_path)
                 for p in all_entries_paths:
                   # s = re.search("[0-9]+-[0-9]+-[0-9]+", e)
                   p_escaped = p.replace(" ","").replace("_","")
                   # id_asset = s.group()
                   if basename_escaped_path == p_escaped:
                       path = basedir_path + os.path.sep + p
                       if not noescape:
                         path = path.replace(" ", "\ ")

                       break
               except Exception:
                   pass

           return path

  def pending_lines_process(self):
    _,pending_lines = self._parser.get_pending_lines(self.logfile_names)
    # print pending_lines
    for l in pending_lines:
     # Mark line as last line processed
     self._parser.save_mark(l)

     entry = self._parser.parse_line(l)
     if entry:
       try:
         entry["retention_days"]=self.retention_days
         
         # Check if entry exist, 
         # if exist, update values
         # else, create new entry in database
         _e = self._dao["DAOEntry"].get_entry(entry["path"])
         if _e:
           self._dao["DAOEntry"].update_entry(entry)
         else:
           self._dao["DAOEntry"].create_entry(entry)
         
         for j in self.jobs:
           _ep = entry["path"]

           entry["path"] = self._fix_path(_ep)

           b = os.popen(j % entry)
           print j % entry
           for l in b.readlines():
             print l.split("\n")[0]
         
       except Exception, e:
         print e

  def create_database(self):
    self._dao["DAOEntry"].create_table()

