ISIS Metadata
=============

The IsisMetadata container is quite straight forward. An ISIS cube file can be the input data source. For a full listing of the available properties on an IsisMetadataObject see :ref:`code_isismetadata`.

The IsisFootPrintBlob container is useful for obtaining metadata information from an ISIS cube file, providing an option to no longer retain that image file. In use, it can be excessive to ship ISIS cubes (that have needed metadata information) AND GeoTiffs (that are the final data product to be shared with users). Luckily, it is quite straighforward to dump the ISIS cube's label (which can then be used with the IsisMetadata) object or a blob of data not contained in the label. For example, using the ISIS command `blobdump`, one can dump the footprint that is the ingestible using the IsisFootPrintBlob container.

.. code-block:: bash

  blobdump name=footprint type=polygon
  
