from unittest.mock import PropertyMock

import pytest
from shapely.geometry import Polygon
import geojson

from unittest.mock import patch, PropertyMock

from amg import databasemetadata as dmd

@pytest.fixture
def database_metadata():
    with patch('amg.databasemetadata.sqlalchemy.create_engine') as cre:
        return dmd.DbMetadata('fake', 'nouri')

@pytest.fixture
def polygon():
    return Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])

def test_bbox(database_metadata, polygon):
    with patch('amg.databasemetadata.DbMetadata.footprint', new_callable=PropertyMock) as mock_footprint:
        mock_footprint.return_value = polygon
        assert database_metadata.bbox == (0.0, 0.0, 1.0, 1.0)

def test_geometry(database_metadata, polygon):
    with patch('amg.databasemetadata.DbMetadata.footprint', new_callable=PropertyMock) as mock_footprint:
        mock_footprint.return_value = polygon
        geo_json = database_metadata.geometry
        try:
            geojson.dumps(geo_json)
        except:
            assert False

def test_centroid(database_metadata, polygon):
    with patch('amg.databasemetadata.DbMetadata.footprint', new_callable=PropertyMock) as mock_footprint:
        mock_footprint.return_value = polygon
        centroid = database_metadata.centroid
        assert centroid.x == 0.5
        assert centroid.y == 0.5

def test_genericsql():
    with patch('amg.databasemetadata.sqlite3') as sql:
        values = [(1,2,3,4),]
        columns = [('a',), ('b',), ('c',), ('d',)]
        sql.connect().cursor().fetchall.return_value = values
        description = PropertyMock(return_value=columns)
        type(sql.connect().cursor()).description = description
    
        gsql = dmd.GenericSQLite('notarealdb.db', 'SELECT * FROM notreal')
        
        columns = [c[0] for c in columns]
        assert gsql.data == dict(zip(columns, values[0]))
        assert gsql.a == 1

def test_genericsql_with_remapper():
    column_remapper = {'a':'foo'}
    with patch('amg.databasemetadata.sqlite3') as sql:
        values = [(1,2,3,4),]
        columns = [('a',), ('b',), ('c',), ('d',)]
        sql.connect().cursor().fetchall.return_value = values
        description = PropertyMock(return_value=columns)
        type(sql.connect().cursor()).description = description
    
        gsql = dmd.GenericSQLite('notarealdb.db', 'SELECT * FROM notreal',
                                 column_remapper=column_remapper)
        
        columns = [c[0] for c in columns]
        assert gsql.foo == 1

def test_genericsql_with_error():
    with patch('amg.databasemetadata.sqlite3') as sql:
        values = [(1,2,3,4),(5,6,7,8)]
        columns = [('a',), ('b',), ('c',), ('d',)]
        sql.connect().cursor().fetchall.return_value = values
        description = PropertyMock(return_value=columns)
        type(sql.connect().cursor()).description = description

        with pytest.raises(ValueError):
            gsql = dmd.GenericSQLite('notarealdb.db', 
                                     'SELECT * FROM notreal')
                                     