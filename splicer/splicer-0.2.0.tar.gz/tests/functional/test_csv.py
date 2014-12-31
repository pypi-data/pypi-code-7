from nose.tools import *

import splicer
from splicer.adapters.dir_adapter import DirAdapter


from .. import fixture_path

def test_csv():

  dataset = splicer.DataSet()
  dataset.add_adapter(
    DirAdapter(
      crime = dict(
        root_dir = fixture_path(),
        pattern = "crime_state_by_state.csv",
        decode = "auto",
        codec_options = dict(
          has_headers = True,
          dialect = 'excel'
        )
      )
    )
  )
  
  count = 0
  for r in  dataset.query('select * from crime limit 10'):
    count += 1
  import pdb; pdb.set_trace()