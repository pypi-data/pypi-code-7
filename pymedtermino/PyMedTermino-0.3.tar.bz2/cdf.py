# -*- coding: utf-8 -*-
# PyMedTermino
# Copyright (C) 2012-2014 Jean-Baptiste LAMY
# LIMICS (Laboratoire d'informatique médicale et d'ingénierie des connaissances en santé), UMR_S 1142
# University Paris 13, Sorbonne paris-Cité, Bobigny, France

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
pymedtermino.cdf
*******************

PyMedtermino module for CDF (Thériaque French drug database).

.. class:: CDF
   
   The CDF terminology. See :class:`pymedtermino.Terminology` for common terminology members; only CDF-specific members are described here.

   A CDF to ICD10 mapping (from Thériaque) is also provided.
"""

__all__ = ["CDF", "connect_to_theriaque_db"]

import sys, os, os.path, psycopg2
import pymedtermino

db = db_cursor = None
def connect_to_theriaque_db(host = "", port = "", user = "theriaque", password = "", db_name = "theriaque", encoding = "latin1"):
  """Connects to a Thériaque PostgreSQL database.
This function **must** be called before using CDF. Default values should be OK for a local Theriaque installation with PostgresQL."""
  global db, db_cursor
  db        = psycopg2.connect(host = host, port = port, database = db_name, user = user, password = password)
  db_cursor = db.cursor()
  
  import atexit
  atexit.register(db.close)
  
  
class CDF(pymedtermino.Terminology):
  def __init__(self):
    pymedtermino.Terminology.__init__(self, "CDF")
    
  def _create_Concept(self): return CDFConcept
  
  def first_levels(self):
    raise NotImplementedError
    
  def search(self, text):
    #db_cursor.execute("SELECT DISTINCT conceptId FROM Description WHERE term LIKE ?", ("%%%s%%" % text,))
    db_cursor.execute("SELECT cdf_numero_pk, cdf_code_pk FROM cdf_codif WHERE cdf_nom LIKE %s", ("%%%s%%" % text.upper(),))
    r = db_cursor.fetchall()
    l = []
    for (numero, code) in r:
      try: l.append(self["%s_%s" % (numero, code)])
      except ValueError: pass
    return l


class CDFConcept(pymedtermino.MultiaxialConcept, pymedtermino._StringCodeConcept):
  """A CDF concept. See :class:`pymedtermino.Concept` for common terminology members; only CDF-specific members are described here.

Additional attributes are available for relations, and are listed in the :attr:`relations <pymedtermino.Concept.relations>` attribute.

.. attribute:: cdf_numero

   The original CDF "numero" code.

.. attribute:: cdf_code

   The original CDF "code".
"""
  
  def __init__(self, code):
    self.cdf_numero, self.cdf_code = code.split("_")
    #db_cursor.execute("SELECT cdf_nom FROM cdf_codif WHERE (cdf_numero_pk = ?) AND (cdf_code_pk = ?)", (self.cdf_numero, self.cdf_code))
    db_cursor.execute("SELECT cdf_nom FROM cdf_codif WHERE cdf_numero_pk = %s AND cdf_code_pk = %s", (self.cdf_numero, self.cdf_code))
    r = db_cursor.fetchone()
    if not r: raise ValueError()
    
    pymedtermino.MultiaxialConcept.__init__(self, code, r[0])
    
  def __getattr__(self, attr):
    if   attr == "parents":
      db_cursor.execute("SELECT cdfpf_numerop_fk_pk, cdfpf_codep_fk_pk FROM cdfpf_lien_cdf_pere_fils WHERE (cdfpf_numerof_fk_pk = %s) AND (cdfpf_codef_fk_pk = %s)", (self.cdf_numero, self.cdf_code))
      self.parents = [self.terminology["%s_%s" % (numero, code)] for (numero, code) in db_cursor.fetchall()]
      return self.parents
      
    elif attr == "children":
      db_cursor.execute("SELECT cdfpf_numerof_fk_pk, cdfpf_codef_fk_pk FROM cdfpf_lien_cdf_pere_fils WHERE (cdfpf_numerop_fk_pk = %s) AND (cdfpf_codep_fk_pk = %s) ORDER BY cdfpf_numord", (self.cdf_numero, self.cdf_code))
      self.children = [self.terminology["%s_%s" % (numero, code)] for (numero, code) in db_cursor.fetchall()]
      return self.children
      
    elif attr == "relations":
      return []
      
    elif attr == "terms":
      return [self.term]
      
    raise AttributeError(attr)



CDF = CDF()

try:    from pymedtermino.icd10 import ICD10
except: ICD10 = None

if ICD10:
  class CDF_2_ICD10_Mapping(pymedtermino.Mapping):
    def __init__(self):
      pymedtermino.Mapping.__init__(self, CDF, ICD10)
      
    def _create_reverse_mapping(self): return ICD10_2_CDF_Mapping()
    
    def map_concepts(self, concepts):
      r = pymedtermino.Concepts()
      for concept in concepts:
        db_cursor.execute("SELECT cimcdf_cim_code_fk_pk FROM cimcdf_cim10_codif WHERE (cimcdf_cdf_numero_fk_pk = %s) AND (cimcdf_cdf_code_fk_pk = %s)", (concept.cdf_numero, concept.cdf_code))
        for (code,) in db_cursor.fetchall():
          if (not "-" in code) and (len(code) > 3): code = "%s.%s" % (code[:3], code[3:])
          c = self.terminology2.get(code)
          if c: r.add(c)
      return r

  class ICD10_2_CDF_Mapping(pymedtermino.Mapping):
    def __init__(self):
      pymedtermino.Mapping.__init__(self, ICD10, CDF)
      
    def _create_reverse_mapping(self): return CDF_2_ICD10_Mapping()
    
    def map_concepts(self, concepts):
      r = pymedtermino.Concepts()
      for concept in concepts:
        code = concept.code.replace(".", "")
        db_cursor.execute("SELECT cimcdf_cdf_numero_fk_pk, cimcdf_cdf_code_fk_pk FROM cimcdf_cim10_codif WHERE cimcdf_cim_code_fk_pk = %s", (code,))
        for (numero, code) in db_cursor.fetchall():
          c = self.terminology2.get("%s_%s" % (numero, code))
          if c: r.add(c)
      return r
      
  cdf_2_icd10 = CDF_2_ICD10_Mapping()
  cdf_2_icd10.register()
  icd10_2_cdf = ICD10_2_CDF_Mapping()
  icd10_2_cdf.register()

  
