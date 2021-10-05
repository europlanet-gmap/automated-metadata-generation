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

class IsisCamInfo(IsisGeomBase):
    """
    This class is the metadata container for the output from
    the ISIS caminfo command. 

    This class uses the IsisGeomBase mixin in case the caminfo command
    has been run with the `polygon=true` flag, in which case a GIS
    footprint is embedded in the data.

    Parameters
    ----------
    datafile : str
               The path to the input ISIS cube file

    Attributes
    ----------
    data : obj
           A pvl.PVLModule object containing the parsed data label
           
    isislabel : str
                The PVL representation of the original ISIS label
                
    label : str
            The PVL representation of the original label, before ingestion
            into ISIS
            
    stats_mean : float
                 The mean DN computed by caminfo

    stats_std : float
                The standard deviation of the DNs as computed by caminfo

    stats_min : float
                The minimum DN value computed by caminfo

    stats_max : float
                The maximum DN value computed by caminfo
    
    target : str
             The target of the observations

    phase_angle : float
                  The angle between the sun and spacecraft at the center of the image

    emisssion_angle : float
                      The angle between the spacecraft and a vector perpendicular (surface normal) to the surface

    incidence_angle : float
                      The angle between the sun and the surface normal at the center of the image

    north_azimuth : float
                    The clockwise angle from the center of the image to true north

    off_nadir : float
                The angle between the spacecraft vector and the look vector

    subsolar_ground_azimuth : float
                              The ground azimuth to the subsolar point

    local_solar_time : float
                       The angle of the sun relative to the center of the image (how
                       high the sun is in the sky)
    
    footprint : obj
                shapely Polygon or MultiPolygon defining the 
                data footprint

    """
    def __init__(self, datafile):
        self.datafile = datafile
        
    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = pvl.load(self.datafile)
        return self._data['Caminfo']

    @property
    def isislabel(self):
        return pvl.dumps(self.data['IsisLabel'], encoder=pvl.encoder.PVLEncoder())
    
    @property
    def label(self):
        return pvl.dumps(self.data['OriginalLabel'], encoder=pvl.encoder.PVLEncoder())
    
    @property
    def stats_mean(self):
        return self.data['Statistics'].get('MeanValue', None)
    
    @property
    def stats_std(self):
        return self.data['Statistics'].get('StandardDeviation', None)
    
    @property
    def stats_min(self):
        return self.data['Statistics'].get('MinimumValue', None)
    
    @property
    def stats_max(self):
        return self.data['Statistics'].get('MaximumValue', None)  
    
    @property
    def target(self):
        return self.data['Geometry'].get('Target', None)

    @property
    def phase_angle(self):
        return self.data['Geometry'].get('PhaseAngle', None)

    @property
    def emission_angle(self):
        return self.data['Geometry'].get('EmissionAngle', None)
    
    @property
    def incidence_angle(self):
        return self.data['Geometry'].get('IncidenceAngle', None)
    
    @property
    def north_azimuth(self):
        return self.data['Geometry'].get('NorthAzimuth', None)
    
    @property
    def off_nadir(self):
        return self.data['Geometry'].get('OffNadir', None)
    
    @property
    def solar_longitude(self):
        return self.data['Geometry'].get('SolarLongitude', None)

    @property
    def subsolar_ground_azimuth(self):
        return self.data['Geometry'].get('SubSolarGroundAzimuth', None)
    
    @property
    def local_solar_time(self):
        return self.data['Geometry'].get('LocalTime', None)  
    
    @property
    def footprint(self):
        fp = wkt.loads(self.data['Polygon'].get('GisFootprint'))
        return fp

    
