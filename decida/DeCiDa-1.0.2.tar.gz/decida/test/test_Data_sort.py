#!/usr/bin/env python
import user, decida, decida.test
from decida.Data import Data

test_dir = decida.test.test_dir()
d = Data()
d.read(test_dir + "data.csv")
d.show()
d.sort("freq")
d.show()
