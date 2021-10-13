import pvl
from shapely import wkt

class IsisGeomBase():
    """
    A mix-in that manages providing access to ISIS geometries, 
    e.g., image footprints.

    Attributes
    ----------
    geometry : dict
               GeoJSON representation of the geometry

    centroid : obj
               shapely point object defining the
               center of the geometry

    bbox : list
           four element geometry bounding box

    footprint : obj
                shapely Polygon or MultiPolygon defining the 
                data footprint
    """
    @property
    def geometry(self):
        return self.footprint.__geo_interface__

    @property
    def centroid(self):
        return self.footprint.centroid
    
    @property
    def bbox(self):
        return self.footprint.bounds
    
    @property
    def footprint(self):
        if not hasattr(self, '_footprint'):
            startbyte = self.data['Polygon']['StartByte'] - 1
            stopbyte = self.data['Polygon']['Bytes']
            with open(self.datafile, 'rb') as f:
                f.seek(startbyte)
                self._footprint = wkt.loads(f.read(stopbyte).decode('UTF-8'))
        return self._footprint

class IsisFootPrintBlob(IsisGeomBase):
    """
    This class parses ISIS footprints that have been dumped from labels
    using the blobdump command.

    This class uses the IsisGeomBase mix-in. Therefore, all attributes
    on that class are available on this class, e.g., footprint.

    Parameters
    ----------
    datafile : path
               The path to the input data file

    Attributes
    ----------
    data : obj
           a pvl.PVLModule object parsed from the input datafile
    """
    def __init__(self, datafile):
        self.datafile = datafile

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = pvl.load(self.datafile)
        return self._data

class IsisMetadata(IsisGeomBase):
    """
    This class is the metadata container for an ISIS cube. 
    
    This class uses the IsisGeomBase mix-in. Therefore, all attributes
    on that class are available on this class, e.g., footprint.

    Parameters
    ----------
    datafile : str
               The path to the input ISIS cube file

    Attributes
    ----------
    data : obj
           A pvl.PVLModule object containing the parsed data label

    longitude_domain : int
                       The longitude domain parsed from the ISIS label
    """
    def __init__(self, datafile):
        self.datafile = datafile
        
    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = pvl.load(self.datafile)
        return self._data

    @property
    def longitude_domain(self):
        try:
            return self.data['IsisCube']['Mapping']['LongitudeDomain']
        except:
            return None
