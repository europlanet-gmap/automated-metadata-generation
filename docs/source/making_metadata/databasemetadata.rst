Database Metadata
=================

Frequently, derived data products may have additional metadata stored in a database. This module supports access to data in a way that is synonymous with the other data containers. The DatabaseMetadata object is currently implemented to just get an objects geometry. In the future this functionality will be expanded.

Here is an example usage:

.. code-block:: python
    :linenos:

    sql = f"""
    WITH cte_geoms AS
        (
        SELECT id, geom FROM kaguyatc
        WHERE 
            kaguyatc.name LIKE ANY (array ['{image_a}%%', '{image_b}%%'])
        )
    SELECT ST_AsText(ST_Extent(ST_Intersection(A.geom, B.geom))) FROM cte_geoms as A, cte_geoms as B
    WHERE A.id > B.id AND A.id != B.id
    """
    db = DbMetadata(database, 'postgresql://uname:password@host:port', sql=sql)

Lines 1-10 define an SQL query that will look for two images in a table named kaguyatc and return the well-known-text representation of the intersection geometry. In line 11, the DatabaseMetadata object is created. When one accesses a geometry on the object (for example via UnifiedMetadata.geometry), the database query is executed and - in the case of this example - the GeoJSON representation of the footprint is returned.

.. note::
  In future iterations of the library we plan to extend support for arbitrary attribute lookups via SQL.
