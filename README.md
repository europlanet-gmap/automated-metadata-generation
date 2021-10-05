<p align="center">
  <img src="docs/AMG_Logo.svg" alt="AMG" width=200> 
</p>

# Automated Metadata Generation (amg)
This project takes metadata from disparate sources, homogenizes them, and then writes out to common metadata formats. Right now, STAC and FGDC metadata writes are supported.

[![Documentation Status](https://readthedocs.org/projects/automated-metadata-generation/badge/?version=latest)](https://automated-metadata-generation.readthedocs.io/en/latest/?badge=latest)

![Build Status](https://github.com/USGS-Astrogeology/automated-metadata-generation/actions/workflows/continuous_integration.yml/badge.svg)

[![codecov](https://codecov.io/gh/USGS-Astrogeology/automated-metadata-generation/branch/master/graph/badge.svg?token=8IX48PO0PI)](https://codecov.io/gh/USGS-Astrogeology/automated-metadata-generation)


## Installation
This is an alpha library, so the only installation is a development install. To install:

- clone this repository
- `cd` into the repository
- and create a conda environment using `conda create -n amg -f environment.yml`
- then activate the conda environment `conda activate amg`
- finally, install this library `python setup.py develop`

## Development Installation
Is identical to the standard installation except the dev environment.yml should be used in the third step:

`conda create -n amg -f environment-dev.yml`

## Example usage:

Here is a simple example (though the source data are not currently available for download to run as if this were a tutorial).

```
import json

from amg.isismetadata import IsisMetadata
from amg.fgdcmetadata import FGDCMetadata
from amg.gdalmetadata import GDALMetadata
from amg.formatters.stac_formatter import to_stac
from amg import UnifiedMetadata

fgdc = FGDCMetadata('sample2.xml')
gd = GDALMetadata('s0413742778.equi.cub')
imd = IsisMetadata('s0413742778.equi.cub')


overrides = {'license': 'PDDL-1.0',
             'missions':['Voyager 1', 'Voyager 2', 'Galileo']}

mappings = {'bbox':IsisMetadata}

record = UnifiedMetadata([fgdc, gd, imd], overrides=overrides, mappings=mappings)
as_stac = to_stac(record)
as_stac.validate()
json.dumps(as_stac.to_dict(), indent=2)
```

In this example three different metadata sources are imported from the amg library: IsisMetadata, FGDCMetadata, GDALMetadata. These three sources are then read into three variables (`fgdc`, `gd`, and `imd`). Each of these classes are a wrapper around an udnerlying I/O API and expose a set of properties with common names when common metadata can be retrieved (e.g., IsisMetadata an GDALMetadata box expose a `bbox` property as both sources can provide information about a data set's spatial bounding box.). 

Next, a dict of overrides are defined. Overrides are used to override default properties on the metadata classes. Effectively, these are hard coded values that supersede any information that might be available via one of the metadata classes.

Then, a dict of mappings are defined. A mapping explicitly identifies which metadata source should be used to get a piece of metadata. In the example above, the code ensures that the `bbox` property comes from the IsisMetadata object and **not** the FGDCMetadata object.

The UnifiedMetadata class is the library's homogenizer that takes in the disparate metadata sources and can then be queried for metadata attributes usining the common metadata vocabulary.

Finally, the `record`, a UnifiedMetadata Object is passed to a `to_stac` function to return a STAC compliant metadata record. This record is valiated using the remote schema and then dumped as JSON.
