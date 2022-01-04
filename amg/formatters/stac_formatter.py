import datetime
import json
import os
from pathlib import PurePosixPath
import string
from urllib.parse import unquote, urlparse
import warnings

import pystac

from dateutil import parser

def populate_datacube_extension(item, obj):
    """
    Populate the cube extension in a STAC metadata record.

    Parameters
    ----------
    item : obj
           The STAC metadata container

    obj : obj
          An amg.UnifiedMetadata object
    """
    from pystac.extensions.datacube import DatacubeExtension

    item = DatacubeExtension.ext(item)
    xdim = {'type':'spatial',
                  'axis':'x',
                  'extent':[obj.bbox[0], obj.bbox[2]],}
    
    ydim = {'type':'spatial',
                'axis':'y',
                'extent':[obj.bbox[1], obj.bbox[3]],}
    
    item.properties['cube:dimensions'] = {'x':xdim,
                                          'y':ydim}

def populate_eo_extension(item, obj):
    """
    Populate the EO extension in a STAC metadata record.

    Parameters
    ----------
    item : obj
           The STAC metadata container

    obj : obj
          An amg.UnifiedMetadata object
    """
    from pystac.extensions.eo import EOExtension, Band

    item = EOExtension.ext(item)
    bands = []
    for bandnumber, band in obj.bands.items():
        b = Band({'name':f'Band {bandnumber}',
                  'common_name':band.name,
                 'center_wavelength':band.center,
                 'full_width_half_max':band.width})
        bands.append(b)
    item.bands = bands

def populate_projection_extension(item, obj):
    """
    Populate the projection extension in a STAC metadata record.

    Parameters
    ----------
    item : obj
           The STAC metadata container

    obj : obj
          An amg.UnifiedMetadata object
    """
    from pystac.extensions.projection import ProjectionExtension

    item = ProjectionExtension.ext(item)

    item.epsg = obj.epsg
    
    if obj.wkt2:
        item.wkt2 = obj.wkt2
    if obj.projjson:
        item.projjson = obj.projjson
    if obj.geometry:
        # TODO: Fix geom to be valid
        #item.ext.projection.geometry = obj.geometry
        pass
    if obj.bbox:
        item.bbox = obj.bbox
    if obj.centroid:
        cnt = obj.centroid
        item.centroid = {'lat':cnt.y, 'lon':cnt.x}
    if obj.extent_y and obj.extent_x:
        item.shape = [obj.extent_y, obj.extent_x]
    if obj.geotransform:
        item.transform = obj.geotransform

def populate_ssys_extension(item, obj):
        item.properties["ssys:targets"] = obj.targets

def populate_viewgeometry_extension(item, obj):
    from pystac.extensions.view import ViewExtension
    item = ViewExtension.ext(item)
    
    if obj.emission_angle:
        item.off_nadir = obj.emission_angle
    if obj.incidence_angle:
        item.incidenace_angle = obj.incidence_angle
    if obj.north_azimuth:
        item.azimuth = obj.north_azimuth
    if obj.subsolar_ground_azimuth:
        item.sun_azimuth = obj.subsolar_ground_azimuth
    if obj.local_solar_time:  # I think this should be local time
        item.sun_elevation = obj.local_solar_time

def populate_assets(assets, obj):
    """
    Populate the assets in a STAC metadata record.

    Parameters
    ----------
    item : obj
           The STAC metadata container

    obj : obj
          An amg.UnifiedMetadata object
    """
    asset_objs = {}
    for asset in assets:
        for key, value in asset.items():
            try:
                substitution_keys = [s[1] for s in string.Formatter().parse(value) if s[1] is not None]
                if substitution_keys:
                    substitution_kwargs = {k:getattr(obj, k) for k in substitution_keys}
                    asset[key] =  value.format(**substitution_kwargs)
            except:
                pass
        asset_objs[asset['key']] = pystac.Asset.from_dict(asset)

    return asset_objs

def populate_scientific_extension(item, obj):
    if obj.doi:
        item.ext.scientific.doi = obj.doi
    if obj.citation:
        item.ext.scientific.citation = obj.citation
    if obj.publications:
        item.ext.scientific.publications = obj.publications

def check_geometry_size(footprint):
    """
    Excessive large geometries are problematic of AWS SQS (max size 256kb) and cause 
    performance issues becuase they are stored in plain text in the JSON
    blob.

    This func reads the geojson and applies a simple heuristic to reduce the
    footprint size through simplification. With each iteration, the geometry
    is simplified by 0.01 degrees.
    
    Parameters
    ----------
    footprint : obj
                A shapely Polygon or MultiPolygon

    Returns
    -------
    geojson : dict
              A geojson representation of the geometry
    """
    geojson = footprint.__geo_interface__
    as_str = json.dumps(geojson)
    geomsize = len(as_str.encode('utf-8'))
    n_iterations = 0
    while geomsize > 125000:
        footprint = footprint.simplify(0.01)
        geojson = footprint.__geo_interface__
        as_str = json.dumps(geojson)
        geomsize = len(as_str.encode('utf-8'))
        n_iterations += 1
    return geojson

extension_lookup = {"https://stac-extensions.github.io/projection/v1.0.0/schema.json": populate_projection_extension,
                    "https://stac-extensions.github.io/datacube/v1.0.0/schema.json": populate_datacube_extension,
                    "https://stac-extensions.github.io/view/v1.0.0/schema.json": populate_viewgeometry_extension,
                    "https://raw.githubusercontent.com/thareUSGS/ssys/main/json-schema/schema.json": populate_ssys_extension, 
                    "https://stac-extensions.github.io/eo/v1.0.0/schema.json": populate_eo_extension}



def to_stac(obj, 
            extensions=["https://stac-extensions.github.io/projection/v1.0.0/schema.json",
                        "https://stac-extensions.github.io/datacube/v1.0.0/schema.json",
                        "https://stac-extensions.github.io/view/v1.0.0/schema.json",
                        "https://raw.githubusercontent.com/thareUSGS/ssys/main/json-schema/schema.json"],
            assets={},
            collection=None):    
    
    """
    This is the primary callable in this module. This function takes an
    amg.UnifiedMetadata object and returns a STAC compliant metadata file.
    
    Parameters
    ----------
    obj : obj
          A UnifiedMetadata object
    
    extensions : list
                 of PySTAC supported extensions

    assets : dict
             A STAC-spec compliant dictionary of assets associated with this 
             metadata record

    collection : str
                 The collection id that this record is associated with
    """

    properties = {}
    
    # Base item
    dt = None
    if obj.start_date == obj.stop_date:
        dt = obj.start_date
        if not isinstance(dt, (datetime.datetime)):
            dt = parser.parse(dt)
    else:
        dt = obj.start_date
        properties['start_datetime'] = obj.start_date
        properties['stop_datetime'] = obj.stop_date
    
    # Required:
    for key in ['title', 'description', 'missions', 'instruments', 'gsd', 'license']:
        if hasattr(obj, key):
            properties[key] = getattr(obj, key)
        
        else:
            warning.warn(f'Passed object is missing key: {key}. The returned object is likely an invalid STAC object.')
    if isinstance(properties['instruments'], str):
        properties['instruments'] = [properties['instruments']]
    """# Providers
    if obj.providers:
        # Step over all the providers
        # If the providers are the same, do something.
        properties['providers'] = []
        for i, provider in enumerate(obj.providers):
            properties['providers'].append({'name':provider.contact_org,
                                            'roles':[]})"""
    
    if hasattr(obj, 'footprint'):
        geometry = check_geometry_size(obj.footprint)
    else:
        warnings.warn('Unable to locate the footprint attribute on the passed object. The STAC file will be invalid.')
        geometry = None    

    item = pystac.Item(id=obj.productid, 
                       geometry=geometry, 
                       bbox=obj.bbox,  
                       datetime=dt,
                       stac_extensions=extensions,
                       href=os.path.join(obj.href,f'{obj.productid}.json'),
                       collection=collection,
                       properties=properties)
    for extension in extensions:
        func = extension_lookup.get(extension)
        if not func:
            warnings.warn(f'Unsupported extension: {extension}. Skipping...')
        func(item, obj)

    #Populate the assets in the item using the passed assets dict
    assets = populate_assets(assets, obj)
    item.assets = assets

    return item
