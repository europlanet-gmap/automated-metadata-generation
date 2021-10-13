.. _user_yamlmetadata:

YAML Metadata
=============

YAML is a plain text markup language. For example:

.. code-block:: yaml

  license: PDDL-1.0
  missions:
    - 'Kaguya SELENE'
  instruments:
    - Kaguya Terrain Camera (TC)
  doi: https://my_doi/####/##abcd##
  href: http://my_awesome_domain.io/my_data
  longitude_domain: 360
  horizontal_accuracy_value: 50

Since the YAML metadata object is a dictionary of `key:value` pairs, anything could be specified in the YAML file. In fact, one could specify all of the metadata associated with a data product as YAML. (Though we have no idea why you would want to do that! See the below warning.)

.. warning::
  A YAML metadata file is a nice way to provide mappings to a UnifiedMetadata object. It is important to be careful though because a YAMLMetadata input and an override are parsed differently on lookup. For an override, the UnifiedMetadata never checks the other data sources. For a YAMLMetadata object it does. So, an override can never collide with another source, but a YAMLMetadata can! In practice, that might mean defining your override in the YAML file and then providing a mappings dictionary to the UnifiedMetadata object.
