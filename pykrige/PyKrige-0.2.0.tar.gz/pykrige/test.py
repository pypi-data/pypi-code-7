import ok
import uk
import numpy as np
import matplotlib.pyplot as plt

data = np.array([[1069209.0, 243400.0, 26.0],
                 [1070962.0, 243239.0, 73.0],
                 [1070957.0, 241845.0, 96.0],
                 [1070767.0, 242652.0, 73.0],
                 [1070063.0, 242374.0, 67.0],
                 [1069440.0, 242201.0, 39.0],
                 [1071851.0, 241678.0, 104.0],
                 [1068668.0, 243391.0, 22.0],
                 [1068897.0, 242501.0, 20.0],
                 [1068128.0, 242816.0, 9.0],
                 [1070878.0, 243820.0, 73.0],
                 [1069805.0, 243729.0, 48.0],
                 [1071428.0, 241868.0, 99.0],
                 [1071012.0, 241572.0, 96.0],
                 [1067493.0, 243015.0, 5.0]])

UK = uk.UniversalKriging(data[:, 0], data[:, 1], data[:, 2], verbose=True)
OK = ok.OrdinaryKriging(data[:, 0], data[:, 1], data[:, 2], verbose=True)

gridx = np.linspace(1067000.0, 1072000.0, 100)
gridy = np.linspace(241500.0, 244000.0, 100)

z_ok, ss_ok = OK.execute(gridx, gridy)
z_uk, ss_uk = UK.execute(gridx, gridy)
print np.amax(z_ok-z_uk)
print np.amax(ss_ok-ss_uk)