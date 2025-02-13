import os
from setuptools import setup, find_packages
from glob import glob

#Grab the README.md for the long description
with open('README.md', 'r') as f:
    long_description = f.read()

def setup_package():
    setup(
        name = "amg",
        version = '1.0.0',
        author = "Jay Laura",
        author_email = "jlaura@usgs.gov",
        description = ("Automated metadata generation"),
        long_description = long_description,
        license = "Public Domain",
        keywords = "Metadata STAC FGDC",
        url = "https://github.com/USGS-Astrogeology/automated-metadata-generation",
        packages=find_packages(),
        package_data={},
        include_package_data=True,
        scripts=[],
        zip_safe=False,
        install_requires=[],
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Topic :: Utilities",
            "License :: Public Domain",
            'Programming Language :: Python :: 3.10',
        ],
    )

if __name__ == '__main__':
    setup_package()
