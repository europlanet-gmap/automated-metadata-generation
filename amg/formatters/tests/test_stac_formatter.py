from collections import namedtuple
from os import name
import pytest
from shapely.geometry import Polygon, Point

from amg.formatters import stac_formatter as sf
from amg.utils import Band

class FakeUMD():
    def __getattr__(self, key):
        if key == 'footprint':
            return Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
        if 'date' in key:
            return '20210101'
        if 'centroid' in key:
            return Point(0,0)
        if 'bands' in key:
            return {2 : Band(2, center=6.78, width= 1.01),
                    10 : Band(10, center=14.88, width=0.87, name='Foo')}
        return key


@pytest.fixture
def umd():
    return FakeUMD()


def test_basic_stac(umd):
    item = sf.to_stac(umd, extensions=[])
    print(item.to_dict())
    
    # Check property setting
    for key in ['title', 'description', 'missions', 'gsd', 'license']:
        assert item.properties[key] == key
    assert item.properties['instruments'] == ['instruments']

    # Check datetime handling
    assert item.properties['datetime'] == '2021-01-01T00:00:00Z'

    # Check geometry
    assert item.geometry == {'type': 'Polygon', 'coordinates': (((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)),)}
    
    # Check self link
    assert item.links[0].rel == 'self'
    assert f'{item.id}.json' in item.links[0].get_href()

def _test_projection(item):
    # Check that the projection has been filled.
    for key in ['proj:epsg', 'proj:wkt2', 'proj:projjson']:
        assert item.properties[key] == key.split(':')[1]

def _test_view(item):
    # Since the internals maintain the ISIS nomenclature, need to use a lookup for key/value testing
    for key, value in {'view:sun_elevation': 'local_solar_time',
                       'view:sun_azimuth': 'subsolar_ground_azimuth',
                       'view:off_nadir': 'emission_angle', 
                       'view:azimuth': 'north_azimuth'}.items():
        assert item.properties[key] == value

def _test_eo(item):
    print(item.properties)
    assert item.properties['eo:bands'] == [{'name': 'Band 2', 'common_name': None, 'center_wavelength': 6.78, 'full_width_half_max': 1.01}, {'name': 'Band 10', 'common_name': 'Foo', 'center_wavelength': 14.88, 'full_width_half_max': 0.87}]

def _test_cube(item):
    assert 'cube:dimensions' in item.properties
    assert item.properties['cube:dimensions']['x'] == {'type': 'spatial', 'axis': 'x', 'extent': ['b', 'o']}

def test_stac_with_projection(umd):
    item = sf.to_stac(umd, extensions=["https://stac-extensions.github.io/projection/v1.0.0/schema.json"])
    _test_projection(item)

def test_stac_with_datacube(umd):
    item = sf.to_stac(umd, extensions=["https://stac-extensions.github.io/datacube/v1.0.0/schema.json"])
    _test_cube(item)

def test_stac_with_view(umd):
    item = sf.to_stac(umd, extensions=["https://stac-extensions.github.io/view/v1.0.0/schema.json"])
    _test_view(item)

def test_stac_with_eo(umd):
    item = sf.to_stac(umd, extensions=["https://stac-extensions.github.io/eo/v1.0.0/schema.json"])
    _test_eo(item)

def test_stac_with_all_default_extensions(umd):
    item = sf.to_stac(umd)
    _test_projection(item)
    _test_cube(item)
    _test_view(item)
    
