import sqlite3

import sqlalchemy
from shapely import wkt
from shapely.geometry import Point

from amg.utils import fix_footprint_domain

class DbMetadata():
    """
    This class connects to a database using SQLAlchemy, uses the sql kwarg
    to execute a query that returns a geometry, loads the geometry into
    a shapely geometry, and finally returns a number of metadata
    properties.

    Arguments
    ---------
    dbname : str
                The name of the database to connect to

    uri : str
            The connection string in the form 
            {databasetype}://{username}:{password}@{host}:{port}
    
    sql : str
            The sql query to execute. This query should return a 
            WKT Geometry

    Attributes
    ----------
    footprint : obj
                shapely Polygon or MultiPolygon

    geometry : dict
                A dictionary containing geojson

    bbox : tuple
            Containing the four elements of the bounding box in
            the form (xmin, ymin, xmax, ymax)

    centroid : obj
                a shapely Point object defining the centroid
                of the footprint
                
    Examples
    --------
    >>> sql = '''
        WITH cte_geoms AS
            (
            SELECT id, geom FROM ctx
            WHERE 
                ctx.name LIKE ANY (array ['B17_016091_2064_XN_26N031W%%', 'P17_007718_2022_XN_22N031W%%'])
            )
        SELECT ST_AsText(ST_Extent(ST_Intersection(A.geom, B.geom))) FROM cte_geoms as A, cte_geoms as B
        WHERE A.id > B.id AND A.id != B.id'''
    >>> db = DbMetadata('dbname', 'postgresql://uname:pw@mydbrui.gov:port', sql=sql)
    >>> db.footprint
    """
    def __init__(self, dbname, uri, sql='SELECT geom FROM images LIMIT 1;'):
        self.engine = sqlalchemy.create_engine(f'{uri}/{dbname}')
        self.sql = sql


    @property
    def footprint(self):
        if not hasattr(self, '_footprint'):
            with self.engine.connect() as connection:
                result = connection.execute(self.sql).fetchone()
                self._footprint = wkt.loads(result[0])
            #self._footprint = fix_footprint_domain(self._footprint)

        return self._footprint

    @property
    def geometry(self):
        return self.footprint.__geo_interface__

    @property
    def bbox(self):
        bbox = [b - 360 if b > 180 else b for b in self.footprint.bounds]
        print('BBOX', bbox)
        return bbox
    
    @property
    def centroid(self):
        x = self.footprint.centroid.x
        if x >= 180:
            x -= 360
        return Point(x, self.footprint.centroid.y)


class GenericSQLite():
    
    """
    A generic interface to a SQLite database. This class expects to be passed
    an SQL query that returns a single row. The columns on the rows are named
    using introspection and the class data attribute is a dict where the keys
    are the column names and the rows are the column values. The column_remapper
    is used to homogenize the column names to the standard amg names.

    Parameters
    ----------
    datafile : str
               The path to the sqlite database

    sql : str
          An SQL query that returns a single row / record

    column_remapper : dict
                      Of DbName:amg_name. See the amg docs for standard 
                      property names
    """
    def __init__(self, datafile, sql, column_remapper={}):
        self.datafile = datafile
        con = sqlite3.connect(self.datafile)
        
        cursor = con.cursor()        
        cursor.execute(sql)
        
        self.data = cursor.fetchall()
        if len(self.data) > 1:
            raise ValueError (f'Expecting the query to return a single row, mappable to a single file for metadata generation. Returned {len(self.data)} records.')
        original_names = [description[0] for description in cursor.description]

        names = []
        for name in original_names:
            if column_remapper.get(name):
                names.append(column_remapper[name])
            else:
                names.append(name)        

        self.data = dict(zip(names, self.data[0]))

        for k, v in self.data.items():
            if v == 'NULL':
                continue
            setattr(self, k, v)
