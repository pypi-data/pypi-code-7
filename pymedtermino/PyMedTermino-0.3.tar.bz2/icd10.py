# -*- coding: utf-8 -*-
# PyMedTermino
# Copyright (C) 2012-2013 Jean-Baptiste LAMY
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
pymedtermino.icd10
******************

PyMedtermino module for ICD10. Currently supports English and French version of ICD10.

.. class:: ICD10
   
   The ICD10 terminology. See :class:`pymedtermino.Terminology` for common terminology members; only ICD10-specific members are described here.
   
"""

__all__ = ["ICD10"]

import os, os.path, sqlite3 as sql_module
import pymedtermino

db        = sql_module.connect(os.path.join(pymedtermino.DATA_DIR, "icd10.sqlite3"))
db_cursor = db.cursor()
#db_cursor.execute("PRAGMA synchronous  = OFF;")
#db_cursor.execute("PRAGMA journal_mode = OFF;")
db_cursor.execute("PRAGMA query_only = TRUE;")

_SEARCH1 = {}
_SEARCH2 = {}
_TEXT1   = {}
_TEXT2   = {}
_CONCEPT = {}
for lang in ["en", "fr", "de"]:
  #_SEARCH1[lang] = "SELECT code FROM Concept WHERE term_%s LIKE ?"         % lang
  #_SEARCH2[lang] = "SELECT DISTINCT code FROM Text WHERE text_%s LIKE ?"   % lang
  _SEARCH1[lang] = "SELECT Concept.code FROM Concept, Concept_fts WHERE Concept_fts.term_%s MATCH ? AND Concept.id = Concept_fts.docid" % lang
  _SEARCH2[lang] = "SELECT DISTINCT Text.code FROM Text, Text_fts WHERE Text_fts.text_%s MATCH ? AND Text.id = Text_fts.docid"          % lang
  _TEXT1  [lang] = "SELECT text_%s FROM Text WHERE id=?"                   % lang
  _TEXT2  [lang] = "SELECT id, text_%s, text_en, dagger, reference FROM Text WHERE code=? AND relation=?" % lang
  _CONCEPT[lang] = "SELECT parent_code, term_%s FROM Concept WHERE code=?" % lang
  
class ICD10(pymedtermino.Terminology):
  def __init__(self):
    pymedtermino.Terminology.__init__(self, "ICD10")
    
  def _create_Concept(self): return ICD10Concept
  
  def first_levels(self):
    return [self[code] for code in ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI", "XXII"]]
  
  def search(self, text):
    #db_cursor.execute(_SEARCH1[pymedtermino.LANGUAGE], ("%%%s%%" % text,))
    db_cursor.execute(_SEARCH1[pymedtermino.LANGUAGE], (text,))
    r1 = db_cursor.fetchall()
    #db_cursor.execute(_SEARCH2[pymedtermino.LANGUAGE], ("%%%s%%" % text,))
    db_cursor.execute(_SEARCH2[pymedtermino.LANGUAGE], (text,))
    r2 = db_cursor.fetchall()
    return [self[code] for (code,) in set(r1 + r2)]
  

class Text(object):
  """A text in an ICD10 definition for a concept (for example, an exclusion, and inclusion, etc)."""
  
  def __init__(self, id, concept, relation, text, text_en, dagger, reference):
    self.id       = id
    self.concept  = concept
    self.relation = relation
    self.text     = text or text_en
    self.dagger   = dagger
    if reference: self.reference = ICD10[reference]
    else:         self.reference = None
    
  def get_translation(self, language):
    """Translates this text in the given language."""
    db_cursor.execute(_TEXT1[language], (self.id,))
    return db_cursor.fetchone()[0]
    
  def __repr__(self):
    return """Text(%s, %s, %s, %s, %s)""" % (repr(self.concept), repr(self.relation), repr(self.text), repr(self.dagger), repr(self.reference), )
  
  
class ICD10Concept(pymedtermino.MonoaxialConcept, pymedtermino._StringCodeConcept):
  """An ICD10 concept. See :class:`pymedtermino.Concept` for common terminology members; only ICD10-specific members are described here.

.. attribute:: dagger
   
.. attribute:: star
   
.. attribute:: morbidity

.. attribute:: mortality1

.. attribute:: mortality2

.. attribute:: mortality3

.. attribute:: mortality4

Additional attributes can be available, and are listed in the :attr:`relations <pymedtermino.Concept.relations>` attribute.

"""
  def __init__(self, code):
    if code.startswith(u"("): code = code[1:-1]
    db_cursor.execute(_CONCEPT[pymedtermino.LANGUAGE], (code,))
    r = db_cursor.fetchone()
    if not r:
      raise ValueError()
    self.parent_code = r[0]
    term             = r[1]
    if not term:
      db_cursor.execute("SELECT term_en FROM Concept WHERE code=?", (code,))
      term = db_cursor.fetchone()[0]
    pymedtermino.MonoaxialConcept.__init__(self, code, term)
    
  def __getattr__(self, attr):
    if   attr == "parents":
      if self.parent_code == "": return []
      self.parents = [self.terminology[self.parent_code]]
      return self.parents
    
    elif attr == "children":
      db_cursor.execute("SELECT code FROM Concept WHERE parent_code=?", (self.code,))
      self.children = [self.terminology[code] for (code,) in db_cursor.fetchall()]
      return self.children
    
    elif attr == "relations":
      db_cursor.execute("SELECT DISTINCT relation FROM Text WHERE code=?", (self.code,))
      self.relations = set(i for (i,) in db_cursor.fetchall())
      return self.relations
    
    elif (attr == "dagger") or (attr == "star"):
      db_cursor.execute("SELECT dagger, star FROM Concept WHERE code=?", (self.code,))
      self.dagger, self.star = db_cursor.fetchone()
      return getattr(self, attr)
    
    elif (attr == "morbidity") or (attr.startswith("mortality")):
      db_cursor.execute("SELECT morbidity, mortality1, mortality2, mortality3, mortality4 FROM Concept WHERE code=?", (self.code,))
      self.morbidity, self.mortality1, self.mortality2, self.mortality3, self.mortality4 = db_cursor.fetchall()
      return getattr(self, attr)
    
    else:
      db_cursor.execute(_TEXT2[pymedtermino.LANGUAGE], (self.code, attr))
      l = [Text(id, self, attr, text, text_en, dagger, reference) for (id, text, text_en, dagger, reference) in db_cursor.fetchall()]
      setattr(self, attr, l)
      return l
    
    raise AttributeError(attr)
  
  def get_translation(self, language):
    db_cursor.execute("SELECT term_%s FROM Concept WHERE code=?" % language, (self.code,))
    return db_cursor.fetchone()[0]

  
ICD10 = ICD10()
