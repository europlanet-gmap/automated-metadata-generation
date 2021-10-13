import warnings

import yaml

class YAMLMetadata():
    """
    This class supports arbitrary yaml encoded metadata.
    
    Instead of providing explicit properties to every 
    attribute that this class could have, a generic
    __get__ magic method is provided that tries to 
    pull the named attribute from this data container.
    
    Parameters
    ----------
    datafile : str
               Path to the datafile to be parsed

    Attributes
    ----------
    data : str
           The path to the input data file
    """

    def __init__(self, datafile):
        self.datafile = datafile

    def __getattr__(self, name):
        try:
            return self.data[name]
        except:
            raise AttributeError

    @property
    def data(self):
        if not hasattr(self, '_data'):
            with open(self.datafile) as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
            self._data = {}
            for k, v in data.items():
                if '-' in k:
                    newk = k.replace('-', '_')
                    self._data[newk] = v
                    warnings.warn('YAML file keys contained "-", while this is valid YAML, it does break this library. Remapping "-" to "_".')
                else:
                    self._data[k] = v
        return self._data
    