
from feature_regrouper import feature_regrouper

from adduct_grouping import assign_adducts

from shoulder_peak_remover import remove_shoulder_peaks, cleanup_peakmap

from feature_detector import run_feature_finder

# cleanup name space:
# ! no del feature_regrouper here as names for the module overlaps with imported function
try:
    del shoulder_peak_remover
except:
    pass

try:
    del adduct_grouping
except:
    pass

try:
    del feature_detector
except:
    pass



# DO NOT TOUCH THE FOLLOWING LINE:
import pkg_resources  # part of setuptools
__version__ = tuple(map(int, pkg_resources.require(__name__)[0].version.split(".")))

try:
    del algorithms
except:
    pass
