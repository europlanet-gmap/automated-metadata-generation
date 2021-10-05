Installation
============

This is a beta library, so the only installation is a development install. To install:

 1. Clone the code repository `git clone https://github.com/USGS-Astrogeology/automated-metadata-generation`
 2. `cd` into the repository
 3. Create a conda environment using `conda env create -n amg -f environment.yml`
 4. Activate the conda environment `conda activate amg`
 5. Install this library `python setup.py develop`

Development Installation
========================
Is identical to the standard installation except the dev environment.yml should be used in the third step:

`conda env create -n amg -f environment-dev.yml`
