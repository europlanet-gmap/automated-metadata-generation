import os
import xml.etree.ElementTree as ET

import pytest

from amg import fgdcmetadata as fgdc

@pytest.fixture
def fgdc_metadata_equi(datadir):
    return fgdc.FGDCMetadata(os.path.join(datadir, 'fgdc_template.xml'), proj='equirect')

@pytest.fixture
def fgdc_metadata_ortho(datadir):
    return fgdc.FGDCMetadata(os.path.join(datadir, 'fgdc_template.xml'), proj='orthogr')

@pytest.fixture
def fgdc_metadata_polarst(datadir):
    return fgdc.FGDCMetadata(os.path.join(datadir, 'fgdc_template.xml'), proj='polarst')

@pytest.fixture
def fgdc_metadata_transmer(datadir):
    return fgdc.FGDCMetadata(os.path.join(datadir, 'fgdc_template.xml'), proj='transmer')

@pytest.fixture
def fgdc_metadata(datadir):
    return fgdc.FGDCMetadata(os.path.join(datadir, 'fgdc_template.xml'))



class TestFGDCMetadata():
    def test__parse_projection(self, datadir):
        md = fgdc.FGDCMetadata(os.path.join(datadir, 'fgdc_template.xml'))
        assert md.projection == 'equirect'
        assert isinstance(md.data, fgdc.EquirectangularFgdcParser)

    
    def test_title(self, fgdc_metadata):
        assert fgdc_metadata.title == 'Injection Ready Title: {image1}'

    def test_description(self, fgdc_metadata):
        assert fgdc_metadata.description == 'Part I. Part II.'

    @pytest.mark.parametrize('dates, expected', 
                             [({'type': 'single', 'values': ['20210521']}, '20210521'),
                              ({'type': 'range', 'values': ['20210521', '20210522']}, '20210521'),
                              ({'type': 'unsupported', 'values': ['mycustomtime']}, 'exception')])
    def test_start_date(self, fgdc_metadata, dates, expected):
        fgdc_metadata.data.dates = dates
        if expected == 'exception':
            with pytest.raises(ValueError) as e:
                fgdc_metadata.start_date == expected

        else:
            assert fgdc_metadata.start_date == expected

    @pytest.mark.parametrize('dates, expected', 
                             [({'type': 'single', 'values': ['20210521']}, '20210521'),
                              ({'type': 'range', 'values': ['20210521', '20210522']}, '20210522'),
                              ({'type': 'unsupported', 'values': ['mycustomtime']}, 'exception')])
    def test_stop_date(self, fgdc_metadata, dates, expected):
        fgdc_metadata.data.dates = dates
        if expected == 'exception':
            with pytest.raises(ValueError) as e:
                fgdc_metadata.stop_date == expected
        else:
            assert fgdc_metadata.stop_date == expected

    def test_updated_date(self, fgdc_metadata):
        assert fgdc_metadata.updated_date == '20210528'

    def test_serialize(self, fgdc_metadata):
        # Has to be called on the data property since this the attribute of the object that
        # contains the logic for serialization.
        xmlstring = fgdc_metadata.data.serialize()
        
        # Test that the output can be serialized.
        try:
            tree = ET.ElementTree(ET.fromstring(xmlstring))
        except:
            assert False

    def test_license(self, fgdc_metadata):
        assert fgdc_metadata.license == 'The distribution liability statement.'

class TestTransverseMercator():

    def test_data(self, fgdc_metadata_transmer):
        data = fgdc_metadata_transmer.data
        assert isinstance(data, fgdc.TransverseMercatorFgcdParser)

class TestEquirectangular():
    
    def test_data(self, fgdc_metadata_equi):
        data = fgdc_metadata_equi.data
        assert isinstance(data, fgdc.EquirectangularFgdcParser)
    

class TestOrthographic():

    def test_data(self, fgdc_metadata_ortho):
        data = fgdc_metadata_ortho.data
        assert isinstance(data, fgdc.OrthographicFgdcParser)

class TestPolarStereographic():

    def test_data(self, fgdc_metadata_polarst):
        data = fgdc_metadata_polarst.data
        assert isinstance(data, fgdc.PolarStereoGraphicFgdcParser)
