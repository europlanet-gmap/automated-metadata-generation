Plaintext Metadata
==================

The plaintext metadata module is catch all for any metadata that is provided in an unstructured, plain text format. Right now, the library supports reading NASA Ames Stereo Pipeline (ASP) pc_align text files.

.. code-block::

  --> Setting number of processing threads to: 4
  Found input nodata value for DEM: -32768
  Max difference:       156.626
  Min difference:       -145.251
  Mean difference:      -3.42138
  StdDev of difference: 12.9565
  Median difference:    -1.56749
  Writing difference file: results_ba/G01_018668_2065_XN_26N188W__B21_017956_2065_XN_26N188W_ba-FINAL_geodiff-diff.csv

The readers in the plaintextmetadata module all parse an input line by line and expose the data provided in each line as a separate field. For example, the median difference can be exposed in this manner. See :ref:`code_plaintextmetadata` for the API to use plaintext objects.
