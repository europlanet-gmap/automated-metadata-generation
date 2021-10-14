from osgeo import osr
from urllib.parse import urljoin
osr.UseExceptions()

from amg.fgdcmetadata import FGDCMetadata

fgdc_to_osr_translation = {'equirect':[
                               ('false_easting',osr.SRS_PP_FALSE_EASTING),
                               ('false_northing',osr.SRS_PP_FALSE_NORTHING),
                               ('standard_parallel',osr.SRS_PP_STANDARD_PARALLEL_1),
                               ('meridian_longitude',osr.SRS_PP_CENTRAL_MERIDIAN)],
                           'polarst':[
                               ('standard_parallel',osr.SRS_PP_LATITUDE_OF_ORIGIN),
                               [('sv_longitude',osr.SRS_PP_LONGITUDE_OF_ORIGIN),
                                ('scale_factor',osr.SRS_PP_SCALE_FACTOR)],
                                ('false_easting',osr.SRS_PP_FALSE_EASTING),
                                ('false_northing',osr.SRS_PP_FALSE_NORTHING)],
                            'orthogr':[
                                ('center_longitude',osr.SRS_PP_CENTRAL_MERIDIAN),
                                ('center_latitude',osr.SRS_PP_LATITUDE_OF_ORIGIN),
                                ('false_easting',osr.SRS_PP_FALSE_EASTING),
                                ('false_northing',osr.SRS_PP_FALSE_NORTHING)],
                            'transmer': [
                                ('center_longitude', osr.SRS_PP_CENTRAL_MERIDIAN),
                                ('origin_latitude', osr.SRS_PP_LATITUDE_OF_ORIGIN),
                                ('scale_factor', osr.SRS_PP_SCALE_FACTOR),
                                ('false_easting', osr.SRS_PP_FALSE_EASTING),
                                ('false_northing', osr.SRS_PP_FALSE_NORTHING)]
                            }

def lookup_projection_name(name):
    """
    Simple dict lookup to take an input name an return a homogenized name.
    """
    name = name.lower()
    if 'equirectangular' in name:
        return 'equirect'
    elif 'polarstereographic' in name:
        return 'polarst'
    elif 'orthographic' in name:
        return 'orthogr'
    elif 'transverse_mercator' in name:
        return 'transmer'
    


def populate_projection_information(template, obj):
    """
    Parse projection information from a UnifiedMetadata obj into an FGDC template.

    Parameters
    ----------
    template : obj
               an FGDC metadata template (FGDCMetadata.data)

    obj : obj
          A UnifiedMetadata object
    """

    srs = obj.srs
    # Get the projection name out of the SRS.
    label_projection_name = srs.GetAttrValue('PROJECTION')
    
    # Attempt to parse the projection name into a known projection name and get the fields to populate
    short_name = lookup_projection_name(label_projection_name)
    fields = fgdc_to_osr_translation.get(short_name, {})
    # Update the template with the data from the projection
    template.projection['name'] = label_projection_name
    for field in fields:
        if isinstance(field, list):
            for subfield in field:
                val = str(srs.GetProjParm(subfield[1]))
                if val is not None:
                    template.projection[subfield[0]] = val
                    break
        else:
            template.projection[field[0]] = str(srs.GetProjParm(field[1]))

    if 'center_longitude' in template.projection.keys() and obj.longitude_domain == 360:
        if float(template.projection['center_longitude']) > 180:
            template.projection['center_longitude'] = str(float(template.projection['center_longitude']) - 360)

def populate_bounding_box(template, obj):
    """
    Parse bounding box information from a UnifiedMetadata obj into an FGDC template.

    Parameters
    ----------
    template : obj
               an FGDC metadata template (FGDCMetadata.data)

    obj : obj
          A UnifiedMetadata object
    """

    template.bounding_box = {'east':obj.bbox[2],
                         'south':obj.bbox[1],
                         'west':obj.bbox[0],
                         'north':obj.bbox[3]}  

    if obj.longitude_domain == 360 and template.bounding_box['west'] > 180:
        # The data are in a 0-360 domain
        template.bounding_box['west'] -= 360
        template.bounding_box['east'] -= 360

    template.bounding_box = {k:str(v) for k,v in template.bounding_box.items()}

def populate_geodetic(template, obj):
    """
    Parse ellipsoid information from a UnifiedMetadata obj into an FGDC template.

    Parameters
    ----------
    template : obj
               an FGDC metadata template (FGDCMetadata.data)

    obj : obj
          A UnifiedMetadata object
    """
    geo = template.geodetic
    
    if geo['inverse_flattening'] == '':
        inverse_flattening = obj.inverse_flattening
        if inverse_flattening == 0:
            inverse_flattening = 1e-6
        geo['inverse_flattening'] = str(inverse_flattening)
    
    if geo['semi_major_axis'] == '':
        geo['semi_major_axis'] = str(obj.semi_major_axis)

def populate_raster_info(template, obj):
    """
    Parse raster metadata information from a UnifiedMetadata obj into an FGDC template.

    Parameters
    ----------
    template : obj
               an FGDC metadata template (FGDCMetadata.data)

    obj : obj
          A UnifiedMetadata object
    """
    template.raster_info = {'dimensions':'Pixel',
                             'column_count':obj.extent_x,
                             'row_count':obj.extent_y,
                             'vertical_count':obj.extent_x,
                             'x_resolution':obj.resolution_x,
                             'y_resolution':obj.resolution_y}
    template.raster_info = {k:str(v) for k,v in template.raster_info.items()}
    
def populate_digital_forms(template, obj):
    """
    Populate the data HREF.

    Parameters
    ----------
    template : obj
               an FGDC metadata template (FGDCMetadata.data)

    obj : obj
          A UnifiedMetadata object
    """
    dfs = template.digital_forms
    for df in dfs:
        df['network_resource'] = urljoin(obj.href, obj.id)
    
def populate_accuracies(template, obj):
    """
    Populate data accuracy information from a UnifiedMetadata obj into an FGDC template.

    Parameters
    ----------
    template : obj
               an FGDC metadata template (FGDCMetadata.data)

    obj : obj
          A UnifiedMetadata object
    """
    if getattr(obj, 'horizontal_accuracy_report', None):
        template.accuracy_horizontal = {'horizontal_accuracy_report': obj.horizontal_accuracy_report,
                                        'horizontal_accuracy_value': str(obj.horizontal_accuracy_value),
                                        'horizontal_accuracy_test_name': obj.horizontal_accuracy_test_name}
    if getattr(obj, 'vertical_accuracy_report', None):
        template.accuracy_vertical = {'vertical_accuracy_report': obj.vertical_accuracy_report,
                                        'vertical_accuracy_value': str(obj.vertical_accuracy_value),
                                        'vertical_accuracy_test_name': obj.vertical_accuracy_test_name}

def to_fgdc(obj):
    """
    This is the priamry function to call in the module. This function takes a UnifiedMetadata object
    and creates a serialized FGDC metadata record.

    Parameters
    ----------
    obj : obj
          A amg.UnifiedMetadata class instance

    Returns
    -------
     : str
       A string encoded FGDC compliant XML metadata file
    """
    template = None
    for s in obj.sources:
        if isinstance(s, FGDCMetadata):
            template = s.data
    
    populate_projection_information(template, obj)
    populate_bounding_box(template, obj)
    populate_raster_info(template, obj)
    populate_digital_forms(template, obj)
    populate_accuracies(template, obj)
    populate_geodetic(template, obj)

    template.planar_distance_units = 'meters'
    template.online_linkages = obj.doi

    if hasattr(obj, 'title'):
        template.title = obj.title
    if hasattr(obj, 'processing_environment'):
        template.processing_environment = obj.processing_environment

    # Add the point of contact section to the template.
    
    template.validate()
    return template.serialize(use_template=False).decode()
