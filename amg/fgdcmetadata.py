import warnings
import xml.etree.ElementTree as ET
from xml.dom import minidom

from gis_metadata.fgdc_metadata_parser import FgdcParser
from gis_metadata.utils import format_xpaths, ParserProperty, COMPLEX_DEFINITIONS, CONTACTS

class BaseCustomParser(FgdcParser):
    """
    A mix-in class that extends the base gis_metadata 
    FgdcParser class to cover more of the FGDC specification.

    This class should not be instantiated independently. Instead, 
    one should use the FGDCMetadata class. When a projection is 
    infered from the input xml file or specified, the projection
    class (e.g., FGDCMetadata.data) will contain all of these 
    extensions to the FgdcParser.
    """

    def _init_data_map(self):
        super(BaseCustomParser, self)._init_data_map()
        
        # Define simple structures
        planar_unit_prop = 'planar_distance_units'
        self._data_map[planar_unit_prop] = 'spref/horizsys/planar/planci/plandu'
        self._metadata_props.add(planar_unit_prop)

        planar_coordinate_representation_prop = 'planar_coordinate_representation'
        self._data_map[planar_coordinate_representation_prop] = 'spref/horizsys/planar/planci/plance'
        self._metadata_props.add(planar_coordinate_representation_prop)
    
        processing_prop = 'processing_environment'
        self._data_map[processing_prop] = 'idinfo/native'
        self._metadata_props.add(processing_prop)

        # Add complex structured
        self._add_geodetic_structure()
        self._add_positional_accuracies()
        self._add_processor_structure()
        self._add_poc_address()

    def _add_geodetic_structure(self):
        # Add GEODETIC structure to data map
        geodetic_definition = {
            'horizontal_datum':'{horizontal_datum}',
            'ellipsoid':'{ellipsoid}',
            'semi_major_axis':'{semi_major_axis}',
            'inverse_flattening':'{inverse_flattening}'
        }
        geodetic_prop = 'geodetic'
        geodetic_xpath = 'spref/horizsys/{geodetic_path}'
        
        self._data_structures[geodetic_prop] = format_xpaths(
            geodetic_definition,
            horizontal_datum=geodetic_xpath.format(geodetic_path='geodetic/horizdn'),
            ellipsoid=geodetic_xpath.format(geodetic_path='geodetic/ellips'),
            semi_major_axis=geodetic_xpath.format(geodetic_path='geodetic/semiaxis'),
            inverse_flattening=geodetic_xpath.format(geodetic_path='geodetic/denflat')
        )
        # Set the root and add getter/setter (parser/updater) to the data map
        self._data_map['_{prop}_root'.format(prop=geodetic_prop)] = geodetic_prop
        self._data_map[geodetic_prop] = ParserProperty(self._parse_complex, self._update_complex)
        
        # Let the parent validation logic know about the two new custom properties
        self._metadata_props.add(geodetic_prop)
    
    def _add_positional_accuracies(self):
        # Add horizontal accuracy
        horizontal_posacc_definition = {'horizontal_accuracy_report':'{horizontal_accuracy_report}',
                                        'horizontal_accuracy_value':'{horizontal_accuracy_value}',
                                        'horizontal_accuracy_test_name':'{horizontal_accuracy_test_name}'
        }
        horizontal_posacc_prop = 'accuracy_horizontal'
        horizontal_posacc_xpath = 'dataqual/posacc/horizpa/{horizontal_posacc_path}'

        self._data_structures[horizontal_posacc_prop] = format_xpaths(
            horizontal_posacc_definition,
            horizontal_accuracy_report=horizontal_posacc_xpath.format(horizontal_posacc_path='horizpar'),
            horizontal_accuracy_value=horizontal_posacc_xpath.format(horizontal_posacc_path='qhorizpa/horizpav'),
            horizontal_accuracy_test_name=horizontal_posacc_xpath.format(horizontal_posacc_path='qhorizpa/horizpae')
        )

        # Set the root and add getter/setter (parser/updater) to the data map
        self._data_map['_{prop}_root'.format(prop=horizontal_posacc_prop)] = horizontal_posacc_prop
        self._data_map[horizontal_posacc_prop] = ParserProperty(self._parse_complex, self._update_complex)
        
        # Let the parent validation logic know about the two new custom properties
        self._metadata_props.add(horizontal_posacc_prop)

        # Add vertical accuracy
        vertical_posacc_definition = {'vertical_accuracy_report':'{vertical_accuracy_report}',
                                        'vertical_accuracy_value':'{vertical_accuracy_value}',
                                        'vertical_accuracy_test_name':'{vertical_accuracy_test_name}'
        }
        vertical_posacc_prop = 'accuracy_vertical'
        vertical_posacc_xpath = 'dataqual/posacc/vertacc/{vertical_posacc_path}'

        self._data_structures[vertical_posacc_prop] = format_xpaths(
            vertical_posacc_definition,
            vertical_accuracy_report=vertical_posacc_xpath.format(vertical_posacc_path='vertaccr'),
            vertical_accuracy_value=vertical_posacc_xpath.format(vertical_posacc_path='qvertpa/vertaccv'),
            vertical_accuracy_test_name=vertical_posacc_xpath.format(vertical_posacc_path='qvertpa/vertacce')
        )

        # Set the root and add getter/setter (parser/updater) to the data map
        self._data_map['_{prop}_root'.format(prop=vertical_posacc_prop)] = vertical_posacc_prop
        self._data_map[vertical_posacc_prop] = ParserProperty(self._parse_complex, self._update_complex)
        
        # Let the parent validation logic know about the two new custom properties
        self._metadata_props.add(vertical_posacc_prop)       

    def _add_processor_structure(self):
        # Add PROCESSOR structure
        contact_definition = {
            'name':'{name}',
            '_name':'{_name}',
            'organization':'{organization}',
            '_organization':'{organization}',
            'position':'{position}',
            'address':'{address}',
            'address_type':'{address_type}',
            'city':'{city}',
            'state':'{state}',
            'postal':'{postal}',
            'country':'{country}',
            'phone':'{phone}',
            'email':'{email}',
            'fax':'{fax}'
        }
        processor_contact_prop = 'processor'
        processor_contact_xpath = 'dataqual/lineage/procstep/proccont/cntinfo/{pc_xpath}'

        self._data_structures[processor_contact_prop] = format_xpaths(
            contact_definition,
            name=processor_contact_xpath.format(pc_xpath='cntperp/cntper'),
            _name=processor_contact_xpath.format(pc_xpath='cntorgp/cntper'),
            organization=processor_contact_xpath.format(pc_xpath='cntperp/cntorg'),
            _organization=processor_contact_xpath.format(pc_xpath='cntorgp/cntorg'),
            position=processor_contact_xpath.format(pc_xpath='cntpos'),
            address=processor_contact_xpath.format(pc_xpath='cntaddr/address'),
            address_type=processor_contact_xpath.format(pc_xpath='cntaddr/addrtype'),
            city=processor_contact_xpath.format(pc_xpath='cntaddr/city'),
            state=processor_contact_xpath.format(pc_xpath='cntaddr/state'),
            postal=processor_contact_xpath.format(pc_xpath='cntaddr/postal'),
            country=processor_contact_xpath.format(pc_xpath='cntaddr/country'),
            phone=processor_contact_xpath.format(pc_xpath='cntvoice'),
            email=processor_contact_xpath.format(pc_xpath='cntemail'),
            fax=processor_contact_xpath.format(pc_xpath='cntfax')
        )

        # Set the root and add getter/setter (parser/updater) to the data map
        self._data_map['_{prop}_root'.format(prop=processor_contact_prop)] = processor_contact_prop
        self._data_map[processor_contact_prop] = ParserProperty(self._parse_complex, self._update_complex)
        
        # Let the parent validation logic know about the two new custom properties
        self._metadata_props.add(processor_contact_prop)

    def _add_poc_address(self):
        # Add PoC Address
        poc_prop = 'point_of_contact'
        poc_prop_xpath = 'idinfo/ptcontac/cntinfo/{poc_xpath}'
        contact_definition = {
            'name':'{name}',
            'organization':'{organization}',
            'position':'{position}',
            'address':'{address}',
            'address_type':'{address_type}',
            'city':'{city}',
            'state':'{state}',
            'postal':'{postal}',
            'country':'{country}',
            'phone':'{phone}',
            'email':'{email}',
            'fax':'{fax}'
        }
        self._data_structures[poc_prop] = format_xpaths(  
            contact_definition,
            name=poc_prop_xpath.format(poc_xpath='cntperp/cntper'),
            organization=poc_prop_xpath.format(poc_xpath='cntperp/cntorg'),
            position=poc_prop_xpath.format(poc_xpath='cntpos'),
            address=poc_prop_xpath.format(poc_xpath='cntaddr/address'),
            address_type=poc_prop_xpath.format(poc_xpath='cntaddr/addrtype'),
            city=poc_prop_xpath.format(poc_xpath='cntaddr/city'),
            state=poc_prop_xpath.format(poc_xpath='cntaddr/state'),
            postal=poc_prop_xpath.format(poc_xpath='cntaddr/postal'),
            country=poc_prop_xpath.format(poc_xpath='cntaddr/country'),
            phone=poc_prop_xpath.format(poc_xpath='cntvoice'),
            email=poc_prop_xpath.format(poc_xpath='cntemail'),
            fax=poc_prop_xpath.format(poc_xpath='cntfax')
        )

        # Set the root and add getter/setter (parser/updater) to the data map
        self._data_map['_{prop}_root'.format(prop=poc_prop)] = poc_prop
        self._data_map[poc_prop] = ParserProperty(self._parse_complex, self._update_complex)
        
        # Let the parent validation logic know about the two new custom properties
        self._metadata_props.add(poc_prop)

    def serialize(self, use_template=False):
        serialized = super(BaseCustomParser, self).serialize(use_template)
        dom_string = minidom.parseString(serialized).toprettyxml(indent='  ', encoding='UTF-8')
        return b'\n'.join([s for s in dom_string.splitlines() if s.strip()])

class TransverseMercatorFgcdParser(BaseCustomParser):
    """
    A custom projection class to support transverse mercator projections
    in the FGDC metadata.
    """

    def _init_data_map(self):
        super(TransverseMercatorFgcdParser, self)._init_data_map()

        # Define PROJECTION as a complext structure
        mp_definition = {
            'name':'{name}',
            'center_longitude':'{center_longitude}',
            'origin_latitude': '{origin_latitude}',
            'scale_factor':'{scale_factor}',
            'false_easting':'{false_easting}',
            'false_northing':'{false_northing}'
        }

        mp_prop = 'projection'
        mp_xpath = 'spref/horizsys/planar/mapproj/{mp_path}'

        # Add PROJECTION structure to data map      
        self._data_structures[mp_prop] = format_xpaths(
            mp_definition,
            name=mp_xpath.format(mp_path='mapprojn'),
            scale_factor=mp_xpath.format(mp_path='transmer/sfctrmer'),
            center_longitude=mp_xpath.format(mp_path='transmer/longcm'),
            origin_latitude=mp_xpath.format(mp_path='transmer/latprjo'),
            false_easting=mp_xpath.format(mp_path='transmer/feast'),
            false_northing=mp_xpath.format(mp_path='transmer/fnorth')
        )

        # Set the root and add getter/setter (parser/updater) to the data map
        self._data_map['_{prop}_root'.format(prop=mp_prop)] = mp_prop
        self._data_map[mp_prop] = ParserProperty(self._parse_complex, self._update_complex)
        
        # Let the parent validation logic know about the two new custom properties
        self._metadata_props.add(mp_prop)

class OrthographicFgdcParser(BaseCustomParser):
    """
    A custom projection class to support orthographic projections 
    in FGDC metadata.
    """     
    def _init_data_map(self):
        super(OrthographicFgdcParser, self)._init_data_map()
        
        # Define PROJECTION as a complex structure
        mp_definition = {
            'name':'{name}',
            'center_longitude':'{center_longitude}',
            'center_latitude': '{center_latitude}',
            'false_easting': '{false_easting}',
            'false_northing': '{false_northing}'
        }
        mp_prop = 'projection'
        mp_xpath = 'spref/horizsys/planar/mapproj/{mp_path}'
        
        # Add PROJECTION structure to data map
        self._data_structures[mp_prop] = format_xpaths(
            mp_definition,
            name=mp_xpath.format(mp_path='mapprojn'),
            center_longitude=mp_xpath.format(mp_path='orthogr/longpc'),
            center_latitude=mp_xpath.format(mp_path='orthogr/latprjc'),
            false_easting=mp_xpath.format(mp_path='orthogr/feast'),
            false_northing=mp_xpath.format(mp_path='orthogr/fnorth')
        )
        
        # Set the root and add getter/setter (parser/updater) to the data map
        self._data_map['_{prop}_root'.format(prop=mp_prop)] = mp_prop
        self._data_map[mp_prop] = ParserProperty(self._parse_complex, self._update_complex)
        
        # Let the parent validation logic know about the two new custom properties
        self._metadata_props.add(mp_prop)

class PolarStereoGraphicFgdcParser(BaseCustomParser):
    """
    A custom projection class to support polar stereographic projections 
    in FGDC metadata.
    """  
    def _init_data_map(self):
        super(PolarStereoGraphicFgdcParser, self)._init_data_map()

        # Define PROJECTION as a complex structure
        mp_definition = {
            'name':'{name}',
            'sv_longitude':'{sv_longitude}',
            'standard_parallel': '{standard_parallel}',
            'scale_factor':'{scale_factor}',
            'false_easting': '{false_easting}',
            'false_northing': '{false_northing}'
        }
        mp_prop = 'projection'
        mp_xpath = 'spref/horizsys/planar/mapproj/{mp_path}'
        
        # Add PROJECTION structure to data map
        self._data_structures[mp_prop] = format_xpaths(
            mp_definition,
            name=mp_xpath.format(mp_path='mapprojn'),
            standard_parallel=mp_xpath.format(mp_path='polarst/stdparll'),
            sv_longitude=mp_xpath.format(mp_path='polarst/svlong'),
            scale_factor=mp_xpath.format(mp_path='polarst/sfprjorg'),
            false_easting=mp_xpath.format(mp_path='polarst/feast'),
            false_northing=mp_xpath.format(mp_path='polarst/fnorth')
        )
        
        # Set the root and add getter/setter (parser/updater) to the data map
        self._data_map['_{prop}_root'.format(prop=mp_prop)] = mp_prop
        self._data_map[mp_prop] = ParserProperty(self._parse_complex, self._update_complex)
        
        # Let the parent validation logic know about the two new custom properties
        self._metadata_props.add(mp_prop)

class EquirectangularFgdcParser(BaseCustomParser):
    """
    A custom projection class to support equirectangular projections 
    in FGDC metadata.
    """
    def _init_data_map(self):
        super(EquirectangularFgdcParser, self)._init_data_map()

        # Define PROJECTION as a complex structure
        mp_definition = {
            'name': '{name}',
            'standard_parallel': '{standard_parallel}',
            'meridian_longitude': '{meridian_longitude}',
            'origin_latitude': '{origin_latitude}',
            'false_easting': '{false_easting}',
            'false_northing': '{false_northing}'
        }
        mp_prop = 'projection'
        mp_xpath = 'spref/horizsys/planar/mapproj/{mp_path}'
        
        # Add PROJECTION structure to data map
        self._data_structures[mp_prop] = format_xpaths(
            mp_definition,
            name=mp_xpath.format(mp_path='mapprojn'),
            standard_parallel=mp_xpath.format(mp_path='equirect/stdparll'),
            meridian_longitude=mp_xpath.format(mp_path='equirect/longcm'),
            origin_latitude=mp_xpath.format(mp_path='equirect/latprjo'),
            false_easting=mp_xpath.format(mp_path='equirect/feast'),
            false_northing=mp_xpath.format(mp_path='equirect/fnorth'),
        )
        
        # Set the root and add getter/setter (parser/updater) to the data map
        self._data_map['_{prop}_root'.format(prop=mp_prop)] = mp_prop
        self._data_map[mp_prop] = ParserProperty(self._parse_complex, self._update_complex)
        
        # Let the parent validation logic know about the two new custom properties
        self._metadata_props.add(mp_prop)

class FGDCMetadata():
    """
    A base container for parsing FGDC metadata. This class
    relies heavily on the gis_metadata project for parsing.

    The class attempts to dynamically generate the projection
    information from either the input data or a user supplied
    projection. 

    Parameters
    ----------
    xmlfile : str
              The path to the FGDC metadata file or tempalte

    proj : ['equirect', 'polarst', 'orthogr']
           An optional projection definition that injects the 
           appropriate projection class (<mapprojn>) into the
           FGDC template.

    Properties
    ----------
    data : obj
           The projection specific object containing all of the
           metadata. Data are accessible via dot notation.
    
    title : str
            The title of the data product.

    description : str
                  The description (abstract + purpose) of the data product.

    start_date : str
                 The starting date the data were collected or generated

    stop_date : str
                The ending date at which time data collection stopped.

    updated_date : str
                   The reported last update of the data

    license : str
              The license or license disclaimer associated with the data
           
    """

    parser_lookup = {'equirect' : EquirectangularFgdcParser,
                     'polarst' : PolarStereoGraphicFgdcParser, 
                     'orthogr': OrthographicFgdcParser,
                     'transmer':TransverseMercatorFgcdParser}

    def __init__(self, xmlfile, proj=None):
        self.xmlfile = xmlfile
        self.projection = proj
        self._parse_projection()

    def _parse_projection(self):
        """
        If a projection is not explicitly defined, attempt
        to parse the projection from the input xmlfile. This
        method steps through the xml, looking for the <mapproj>
        key and then dynamically loads an appropriate projection
        class (above) if available.
        """

        if self.projection is None:
        # use the xml dom to parse and GetElementTagByName to determine which parser to load.
            tree = ET.parse(self.xmlfile)
            root = tree.getroot()
            mapproj_nodes = tree.findall('./spref/horizsys/planar/mapproj')
            if len(mapproj_nodes) > 1:
                warnings.warn('More than one mapproj key found. Defaulting to the first entry in the XML template.')
            mapproj_node = mapproj_nodes[0]
            for child in list(mapproj_node):
                if child.tag == 'mapprojn':
                    continue
                else:
                    self.projection = child.tag
            if self.projection is None:
                warnings.warn('Unknown projection. Please either include a projection section in the template or supply a projection name explicitly on construction.')

    @property
    def data(self):
        if not hasattr(self, '_data'):
            Parser = self.parser_lookup[self.projection]
            with open(self.xmlfile, 'r') as metadata:
                self._data = Parser(metadata)
        return self._data
    
    @property
    def title(self):
        return self.data.title
    
    @property    
    def description(self):
        return self.data.abstract + ' ' + self.data.purpose

    @property 
    def start_date(self):
        dates = self.data.dates
        if dates['type'] == 'range':
            return dates['values'][0]
        elif dates['type'] == 'single':
            return dates['values'][0]
        else:
            print(dates)    
            raise ValueError('Driver needs to be updated to support a non-range date type')
    
    @property 
    def stop_date(self):
        dates = self.data.dates
        if dates['type'] == 'range':
            return dates['values'][1]
        if dates['type'] == 'single':
            return dates['values'][0]
        else:
            raise ValueError('Driver needs to be updated to support a non-range date type')
    
    @property 
    def updated_date(self):
        return self.data.publish_date
    
    @property 
    def license(self):
        return self.data.dist_liability
    
    #TODO: Add support for providers
    """@property 
    def providers(self):
        providers = []
        distribution_provider = Provider(name=self.data.dist_contact_person,
                                         role='host',
                                         address=self.data.dist_address,
                                         city=self.data.dist_city,
                                         state=self.data.dist_state,
                                         postal_code=self.data.dist_postal,
                                         country=self.data.dist_country,
                                         contact_org=self.data.dist_contact_org,
                                         email=self.data.dist_email,
                                         phone=self.data.dist_phone)
        
        providers.append(distribution_provider)
        
        if hasattr(self.data, 'contacts'):
            for contact in self.data.contacts:
                providers.append(Provider(name=contact['name'],
                                          contact_org=contact['organization'],
                                          email=contact['email']))
        
        return providers"""
