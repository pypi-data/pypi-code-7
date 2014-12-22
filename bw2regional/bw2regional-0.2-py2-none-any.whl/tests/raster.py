from osgeo import gdal
from osgeo.gdalconst import GDT_Float32
import numpy as np

PROJECTION = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]'


def create_raster(filepath, nx=2, ny=2, array=None):
    # Write new, empty raster
    driver = gdal.GetDriverByName('GTiff')
    out = driver.Create(filepath, nx, ny, 1, GDT_Float32, [])
    out.SetProjection(PROJECTION)
    out.SetGeoTranform((0., 1., 0., 0., 0., -1.))
    band = out.GetRasterBand(1)
    band.SetNoDataValue(-1.)
    if array is None:
        array = np.zeros((ny, nx))
    band.WriteArray(array)
    band.FlushCache()
    band = None
    out = None
    return filepath
