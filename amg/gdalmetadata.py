import json
import os
from osgeo import gdal, osr
import pyproj

from amg.utils import Band

gdal.UseExceptions()
osr.UseExceptions()

class GDALMetadata():
    """
    This class wraps GDAL accessible data files and makes
    homogenizes access to metadata elements.

    Parameters
    ----------
    datafile : str
               The path to the datafile to read

    Attributes
    ----------
    data : obj
           THe GDAL object returned by a gdal.Open call

    productid : str
                The name of the product without file extension

    srs : obj
          The spatial reference objected through which spatial reference
          metadata are accessible

    crs : obj
          A pyproj projection object

    projstr : str
              A proj4 projection string

    projjson : dict
               The projection string in JSON format

    wkt2 : str
           The projection string in wkt2 format

    epsg : int
           THe inferred EPSG code for the data. This is often
           incorrect for planetary data.

    extent_x : int
               The dataset size in the x direction
    
    extent_y : int
               THe dataset size in the y direction

    extent_z : int
               THe number of bands or dataset size in the z direction

    geotransform : list
                   The six element affine geotransformation

    resolution_x : float
                   The pixel resolution in the x direction

    resolution_y : float
                   The pixel resolution in the y direction

    gsd : float
          The reported ground sample distance

    bands : list
            of band objects that contain band dependent metadata, e.g., min/max data values

    longitude_origin : float
                       The projection lon origin

    inverse_flattening : float
                         The ellipsoid inverse flattening.
    
    semi_major_axis : float
                      The semi-major axis of the body in GDAL reported units.

    bbox : list
           Four element bounding box coordinates
    """
    def __init__(self, datafile):
        self.datafile = datafile
    
    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = gdal.Open(self.datafile)
        return self._data
    
    @property
    def productid(self):
        basename = os.path.basename(self.datafile)
        return os.path.splitext(basename)[0]
    
    @property 
    def srs(self):
        return self.data.GetSpatialRef()
    
    @property
    def crs(self):
        if self.projstr:
            return pyproj.CRS.from_proj4(self.projstr)
    
    @property
    def projstr(self):
        if self.srs:
            return self.srs.ExportToProj4()
    
    @property
    def projjson(self):
        if self.crs:
            return json.loads(self.crs.to_json())
    
    @property
    def wkt2(self):
        if self.srs:
            return json.dumps(self.srs.ExportToWkt())
    
    @property
    def epsg(self):
        try:
            return self.srs.AutoIdentifyEPSG()
        except:
            return None
    
    @property
    def extent_x(self):
        return self.data.RasterXSize
    
    @property
    def extent_y(self):
        return self.data.RasterYSize
    
    @property
    def extent_z(self):
        return self.data.RasterCount
    
    @property
    def geotransform(self):
        return self.data.GetGeoTransform()
    
    @property
    def resolution_x(self):
        return self.geotransform[1]
    
    @property
    def resolution_y(self):
        return -self.geotransform[5]
    
    @property
    def gsd(self):
        return max(self.resolution_x, -self.resolution_y)

    @property
    def bands(self):
        if not hasattr(self, '_bands'):
            self._bands = []
            for i in range(self.extent_z):
                print('Band', i)
                band = self.data.GetRasterBand(i+1)  # Band counts are 1 based
                band_min = band.GetMinimum()
                band_max = band.GetMaximum()
                band_min, band_max, _, _ = band.GetStatistics(0, 1)
                unittype = band.GetUnitType()
                print(band_min, band_max, unittype)
                self._bands.append(Band(bid=i,
                                        values=[band_min, band_max],
                                        unit = unittype
                                       ))
        return self._bands

    @property
    def longitude_origin(self):
        return self.srs.GetProjParm(osr.SRS_PP_CENTRAL_MERIDIAN)        
        
    @property
    def inverse_flattening(self):
        return self.srs.GetInvFlattening()

    @property 
    def semi_major_axis(self):
        return self.srs.GetSemiMajor()
        
    @property
    def bbox(self):
        bbox = []
        gt = self.geotransform
        for x,y in [(0,0),(self.extent_x, self.extent_y)]:
            nx = gt[0] + x*gt[1] + y*gt[2]
            ny = gt[3] + y*gt[5] + x*gt[4]
            bbox.append(nx)
            bbox.append(ny)
        return bbox