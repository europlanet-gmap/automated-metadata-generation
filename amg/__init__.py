import warnings

__version__ = '1.0.0'

class UnifiedMetadata():
    """

    This class is the primary means by which this library is intended
    to be used. Specifically, this class takes a number of other
    metadata objects from disparate sources and seeks to homogenize 
    the input data into a single container.

    This class overrides attribute lookups (__getattr__) and uses the
    following logic in order to find a given attribute:

    1. If the attribute is provided in the overrides dict, return the value
    for the given key.

    2. If the attribute is in the mappings dict, the user has specified that
    the value should come from a specific source. Perform the attribute lookup
    on that source.
    
    3. Iterate over each source in the input sources list and build a dict
    of found attributes where the key is source and the value is the returned value.
    For example: {'SourceA':'foo', 'SourceB':'foo', 'SourceC':'bar}.
    
    4. If the previous step returns more than one instance of the source, warn the user
    and request that a mapping be provided to disambiguate the metadata source.
    
    5. If the attribute can not be found, warn the user.
    
    6. Return the attribute requested to the caller.

    Parameters
    ----------
    overrides : dict
                in the form {'key':'value'}

    mappings : dict
               in the form {'key':class}, where class is one of the class definitions passed
               in the sources list (e.g., IsisMetadata or GDALMetadata)

    """

    def __init__(self, sources, overrides={}, mappings={}):
        self.sources = sources
        self.overrides = overrides            
        self.mappings = mappings
        
    def __getattr__(self, attr):
        # If we override the attribute, get the override        
        if attr in self.overrides:
            return self.overrides[attr]
        
        # If the user explicitly defines where the data comes from, return that
        if attr in self.mappings.keys():
            for source in self.sources:
                if isinstance(source, self.mappings[attr]):
                    return getattr(source, attr)
        
        # If the user has not defined where the data comes from, seek for it
        values = {}
        for source in self.sources:
            try:
                if hasattr(source, attr):
                    value = getattr(source, attr)
                    values[source] = value
            except: continue
        
        # If more than one source delivers a piece of metadata, alert the user.
        if len(values) > 1:
            warnings.warn(f'Able to find the attribute "{attr}" in more than one data source. The user should get this value explicitly using the mapping kwarg. The values are: {values}.')
        elif len(values) == 0:
            warnings.warn(f'Unable to find the attribute "{attr}" in any data source.')
            return None
        else:
            return values[list(values.keys())[0]]
