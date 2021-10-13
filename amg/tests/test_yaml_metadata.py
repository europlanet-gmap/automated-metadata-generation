import pytest

from amg import yamlmetadata as ymd

@pytest.fixture
def yaml_metadata(datadir):
    return ymd.YAMLMetadata(datadir.join('test_data.yaml'))

def test_yaml_attributes(yaml_metadata):
    assert yaml_metadata.pi == 3.14159
    assert yaml_metadata.xmas == True
    
    # This is a weird accessor because the has a hyphen
    assert len(yaml_metadata.calling_birds) == 4
    assert yaml_metadata.french_hens == 3