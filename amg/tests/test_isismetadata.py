import datetime
import os

import geojson
import pvl
import pytest
import shapely

from amg import isismetadata as imd

@pytest.fixture
def isis_footprintblob(datadir):
    return imd.IsisFootPrintBlob(os.path.join(datadir, 'footprintblob.wkt'))

@pytest.fixture
def isis_cubelabel(datadir):
    return imd.IsisMetadata(os.path.join(datadir, 'cube.label'))

@pytest.fixture
def isis_cubelabel_multispectral(datadir):
    return imd.IsisMetadata(os.path.join(datadir, 'multispectral_cube.label'))

@pytest.fixture
def isis_caminfolabel(datadir):
    return imd.IsisCamInfo(os.path.join(datadir, 'caminfo.pvl'))

@pytest.fixture
def isis_caminfolabel_nogeom(datadir):
    return imd.IsisCamInfo(os.path.join(datadir, 'caminfo_nogeom.pvl'))

class TestIsisFootprintBlob():

    def test_data(self, isis_footprintblob):
        data = isis_footprintblob.data
        assert isinstance(data, pvl.PVLModule)

    def test_footprint(self, isis_footprintblob):
        footprint = isis_footprintblob.footprint
        assert isinstance(footprint, (shapely.geometry.polygon.Polygon,
                                    shapely.geometry.multipolygon.MultiPolygon))

    def test_geometry(self, isis_footprintblob):
        geojson_dict = isis_footprintblob.geometry
        # Test that valid geojson is coming out by serializing
        # using a third party library.
        try:
            geojson_str = geojson.dumps(geojson_dict)
        except:
            assert False

    def test_centroid(self, isis_footprintblob):
        centroid = isis_footprintblob.centroid 
        assert centroid.x == pytest.approx(138.98635)
        assert centroid.y == pytest.approx(9.40386)

    def test_bbox(self, isis_footprintblob):
        assert isis_footprintblob.bbox == (132.0375443856883, 
                                        -0.1143492780517991, 
                                        147.13550355857274, 
                                        16.668013305236155)

class TestIsisMetadata():

    def test_data(self, isis_cubelabel):
        data = isis_cubelabel.data
        assert isinstance(data, pvl.PVLModule)

    def test_longitude_domain(self, isis_cubelabel):
        assert isis_cubelabel.longitude_domain == 360

    def test_missing_longitude_domain(self, isis_cubelabel):
        data = isis_cubelabel.data
        del data['IsisCube']['Mapping']['LongitudeDomain']
        assert isis_cubelabel.longitude_domain == None

    def test_bands_multispectral(self, isis_cubelabel_multispectral):
        bands = isis_cubelabel_multispectral.bands
        assert bands[2].bid == 2
        assert bands[2].center == 6.78
        assert bands[2].width == 1.01

    def test_bands(self, isis_cubelabel):
        bands = isis_cubelabel.bands
        assert bands[1].bid == 1
        assert bands[1].name == 'CLEAR'
        assert bands[1].center == 0.611
        assert bands[1].width == 0.44

class TestIsisCamInfo():

    def test_data(self, isis_caminfolabel):
        data = isis_caminfolabel.data
        print(type(data))
        # PVLObject because the code steps into the 'Caminfo' PVLModule
        assert isinstance(data, pvl.PVLObject)

    def test_isislabel(self, isis_caminfolabel):
        isislabel = isis_caminfolabel.isislabel
        assert 'BEGIN_OBJECT = IsisCube' in isislabel

    def test_originallabel(self, isis_caminfolabel):
        originallabel = isis_caminfolabel.label
        assert 'PDS_VERSION_ID                 = PDS3;' in originallabel

    def test_stats_mean(self, isis_caminfolabel):
        assert isis_caminfolabel.stats_mean == 4.4850017705493

    def test_stats_std(self, isis_caminfolabel):
        assert isis_caminfolabel.stats_std == 3.470610515188

    def test_stats_min(self, isis_caminfolabel):
        assert isis_caminfolabel.stats_min == -273.0

    def test_stats_max(self, isis_caminfolabel):
        assert isis_caminfolabel.stats_max == 41.093

    def test_target(self, isis_caminfolabel):
        assert isis_caminfolabel.target == 'MOON'

    def test_phase_angle(self, isis_caminfolabel):
        assert isis_caminfolabel.phase_angle == 81.765924928992

    def test_emission_angle(self, isis_caminfolabel):
        assert isis_caminfolabel.emission_angle == 14.733877019508

    def test_incidence_angle(self, isis_caminfolabel):
        assert isis_caminfolabel.incidence_angle == 79.794593365301

    def test_north_azimuth(self, isis_caminfolabel):
        assert isis_caminfolabel.north_azimuth == 89.342277203456

    def test_off_nadir(self, isis_caminfolabel):
        assert isis_caminfolabel.off_nadir == 13.80783306372

    def test_solar_longitude(self, isis_caminfolabel):
        assert isis_caminfolabel.solar_longitude == 156.57991225668

    def test_subsolar_ground_azimuth(self, isis_caminfolabel):
        assert isis_caminfolabel.subsolar_ground_azimuth == 277.28214288415

    def test_local_solar_time(self, isis_caminfolabel):
        assert isis_caminfolabel.local_solar_time == 17.166849212264

    def test_footprint(self, isis_caminfolabel):
        footprint = isis_caminfolabel.footprint
        assert isinstance(footprint, (shapely.geometry.polygon.Polygon,
                                    shapely.geometry.multipolygon.MultiPolygon))

    def test_start_date(self, isis_caminfolabel):
        expected = datetime.datetime.strptime('2008-07-17T20:15:35.150081', '%Y-%m-%dT%H:%M:%S.%f')
        assert isis_caminfolabel.start_date == expected

    def test_stop_date(self, isis_caminfolabel):
        expected = datetime.datetime.strptime('2008-07-17T20:16:05.413806', '%Y-%m-%dT%H:%M:%S.%f')
        assert isis_caminfolabel.stop_date == expected

    def test_no_footprint(self, isis_caminfolabel_nogeom):
        with pytest.raises(KeyError):
            isis_caminfolabel_nogeom.footprint