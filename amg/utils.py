import datetime
import glob
import json
import os
from typing import Sequence

import numpy as np
from shapely.ops import split
from shapely.affinity import translate
from shapely.geometry import LineString, MultiPolygon


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.int64):
            return int(obj)
        if isinstance(obj, datetime.datetime):
            return obj.__str__()
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        if isinstance(obj, set):
            return sorted(list(obj))
        return json.JSONEncoder.default(self, obj)

def fix_footprint_domain(footprint):
    geoms = split(footprint, LineString([[180, -90], [180,90]]))
    
    for geom in geoms:
        if (np.asarray(geom.exterior.coords.xy[0]) > 180).any():
            geom = translate(geom, xoff=-360)

    return geom

def find_file(*path: Sequence[str]) -> str:
    """
    Find a single file along a given PATH.

    Parameters
    ----------
    path : list
           of strings defining a path and any search
           wildcards

    Returns
    -------
    found : str
            The path of the file found

    Examples
    --------
    >>> paths = ['/home/user/', '*.txt']
    >>> found = find_file(paths)
    >>> print(found)
    >>> myfile.txt
    """
    found = find_files(*path)
    if len(found) != 1:
        return
    return found[0]

def find_files(*path: Sequence[str]) -> list:
    """
    Find a single file along a given PATH.

    Parameters
    ----------
    path : list
           of strings defining a path and any search
           wildcards

    Returns
    -------
    found : list
            of files found at the given path matching the search string
            """
    return glob.glob(os.path.join(*path))

def write_fgdc(path: str, fgdc_md: str):
    """
    Write an fgdc metadata string to a given path.

    Parameters
    ----------
    path : str
           The path to write the file to
    
    fgdc_md : str
              The serialized fgdc metadata
    """
    with open(path, 'w') as f:
        f.write(fgdc_md)
    
def write_stac(path: str, stac_md: dict):
    """
    Write a stac metadata dictioanry to a path
    using json dump and pretty formatting (indentation).

    Parameters
    ----------
    path : str
           THe path to write the file to

    stac_md : dict
              A json serializable stac metadata dict
    """
    stac_dict = stac_md.to_dict()
    with open(path, 'w') as f:
        json.dump(stac_dict, f, indent=2, cls=JsonEncoder)

# TODO: Homogenize providers internal to amg
"""class Provider():
    def __init__(self, name='',
                 role=None, 
                 url=None, 
                 address=None, 
                 city=None,
                 postal_code=None,
                 state=None, 
                 country=None,
                 contact_org=None,  
                 contact_person=None, 
                 email=None,
                 phone=None):
    
        self.name = name
        self.role = role
        self.url = url
        self.address = address
        self.city = city
        self.data = state
        self.postal_code = postal_code
        self.country = country
        self.contact_org = contact_org
        self.contact_person = contact_person
        self.email = email
        self.phone = phone"""

#TODO: Hmogenize band information
class Band():
    """
    A data container for storing band dependent metadata.
    """

    def __init__(self, 
                 bid, 
                 extent_x=None, 
                 extent_y=None,
                 values=[],
                 reference_system=None,
                 step=None,
                 unit=None):
        
        self.bid = bid
        self.extent_x = extent_x
        self.extent_y = extent_y
        self.values = values
        self.reference_system = reference_system
        self.step = step
        self.unit = unit
        
    def __repr__(self):
        attrs = {'bandid':self.bid,
                 'extent_x':self.extent_x,
                 'extent_y':self.extent_y,
                 'values':self.values,
                 'reference_system':self.reference_system,
                 'step':self.step,
                 'unit':self.unit}
        return json.dumps(attrs)
