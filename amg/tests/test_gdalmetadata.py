import json

from amg.gdalmetadata import GDALMetadata
import pytest
from unittest.mock import patch

class FakeSRS():
    def ExportToWkt(self):
        return {'srs':'the spatial reference'}

    def AutoIdentifyEPSG(self):
        return 94900

    def ExportToProj4(self):
        return json.dumps({"projstring":"here it is"})

    def GetProjParm(self, arg):
        return arg

    def GetInvFlattening(self):
        return 0

    def GetSemiMajor(self):
        return 1000

class FakeCRS():
    def to_json(self):
        return json.dumps({"loaded from pyproj": "projstring"})

class FakeGDAL():
    def GetSpatialRef(self):
        return FakeSRS()

    @property
    def RasterXSize(self):
        return 10

    @property
    def RasterYSize(self):
        return 10

    @property
    def RasterCount(self):
        return 1

    def GetGeoTransform(self):
        return [0,1,2,3,4,5]

@pytest.fixture
def gdm():
    with patch('amg.gdalmetadata.gdal.Open') as gdalopen:
        with patch('amg.gdalmetadata.pyproj.CRS.from_proj4') as proj4:
            gdalopen.return_value = FakeGDAL()
            proj4.return_value = FakeCRS()
            gdm = GDALMetadata('my/fake/spatialdata.tif')
            yield gdm

def test_productid(gdm):
    assert gdm.productid == 'spatialdata'

def test_gdal_wkt2(gdm):
    assert gdm.wkt2 == '{"srs": "the spatial reference"}'

def test_srs(gdm):
    assert isinstance(gdm.srs, FakeSRS)

def test_epsg(gdm):
    assert gdm.epsg == 94900

def test_no_epsg():
    gdm = GDALMetadata('fake.tif')
    assert gdm.epsg == None

def test_projstr(gdm):
    assert gdm.projstr == '{"projstring": "here it is"}'

def test_crs(gdm):
    assert isinstance(gdm.crs, FakeCRS)

def test_projjson(gdm):
    assert gdm.projjson == {"loaded from pyproj": "projstring"}

def test_extent_x(gdm):
    assert gdm.extent_x == 10

def test_extent_y(gdm):
    assert gdm.extent_y == 10

def text_extent_z(gdm):
    assert gdm.extent_z == 1

def test_geotransform(gdm):
    assert gdm.geotransform == [0,1,2,3,4,5]

def test_resolution_x(gdm):
    assert gdm.resolution_x == 1

def test_resolution_y(gdm):
    assert gdm.resolution_y == -5

def test_gsd(gdm):
    assert gdm.gsd == 5

def test_longitude_origin(gdm):
    assert gdm.longitude_origin == 'central_meridian'

def test_inverse_flattening(gdm):
    assert gdm.inverse_flattening == 0

def test_semi_major_axis(gdm):
    assert gdm.semi_major_axis == 1000