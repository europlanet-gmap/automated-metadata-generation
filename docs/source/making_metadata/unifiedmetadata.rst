Unified Metadata
================

The UnifiedMetadata object is the data access layer for users of this library. All of the other containers are pushed into the UnifiedMetadata object and this class acts as a giant lookup dictionary.

The UnifiedMetadata objet supports two key concepts: `mappings` and `overrides`.

Mappings
--------
A mapping is a declaration that tells the UnifiedMetadata object where to get a specific piece of metadata. For example, support one had an IsisMetadata object and a GDALMetadata object as inputs. Both declare a bbox (bounding box). Which one should be used?

.. code-block:: python
    :linenos:

    imd = IsisMetadata('my_cube.cub')
    gd = GDALMetadata('my_tif.tif')

    umd = UnifiedMetadata([imd, gd])

If one runs the above example and attempts to access the bbox (`umd.bbox`), a warning will be returned because the `bbox` is ambiguous (i.e., it could come from two sources). A mapping can be used to tell the UnifiedMetadata object which source to use.

.. code-block:: python
  :linenos:
  
  imd = IsisMetadata('my_cube.cub')
  gd = GDALMetadata('my_tif.tif')

  mappings = {'bbox':IsisMetadata}
  umd = UnifiedMetadata([imd, gd], mappings=mappings)

Overrides
---------
Overrides are used to either force a particular value to a given key or to explicitly define a value. Let's look at an example:

.. code-block:: python
    :linenos:

    gd = GDALMetadata('my_tif.tif')
  
    overrides = {'href':'http://where_is_my_data/my_tif.tif'}

    umd = UnifiedMetadata([gd]

GDAL does not have any information about the ultimate, online location of your data. Both FGDC (<networkr>) and STAC (assets.self) would like the online location of the data provided. Since, the `href` is a missing key, one can use the overrides to provide that information.

.. note::
  Alternatively, is it possible to write a single YAML file that contains the key:value pairs and pass that in as another data source. See :ref:`user_yamlmetadata` for an example.
