"""
Scientific Python Netcdf Reader class file

This reader uses the Scientific Python library to access a netcdf file.  This isn't installed in
arcgis python by default, but this class is faster.

@author: Robert Toomey (retoomey)
"""  
import Scientific.IO.NetCDF
from w2py import log

import netcdf_reader

class sciNetcdfReader(netcdf_reader.netcdfReader):
    
    def __init__(self, datafile):
        """ Open NetCDF file with Scientific Python library
        """
        log.info("Trying to read netcdf "+datafile)
        try:
            self.data = Scientific.IO.NetCDF.NetCDFFile(datafile, "r")
        except BaseException as e:
            log.error("Couldn't read netcdf data from file "+datafile)
            log.error("Exception {0}".format(e))
    
    def haveDimension(self, dim):
        return hasattr(self.data, dim)
    
    def haveAttribute(self, param1, param2):
        if param1 == "":
            return hasattr(self.data, param2)
        else:
            return False
    
    #def getAttributeNames(self, params):
    #    print self.data.attributes
    #    print dir(self.data)
    #    return self.data.attributes
    
    def getAttributeValue(self, param1, param2):
        # "" for param1 is global attribute, otherwise variable
        if param1 == "":
            return getattr(self.data, param2)
        else:
            var = self.data.variables.get(param1)
            return getattr(var, param2)
    
    def getDimensionSize(self, param1):
        return int(self.data.dimensions[param1])
    
    def getDimensionSizeByVariable(self, param1):
        v = self.data.variables.get(param1)
        key = v.dimensions[0]
        return int(self.data.dimensions[key]) 
    
    def getValueLookup(self, param1):
        # In Sci we use the actual variable object values 
        return self.data.variables.get(param1).getValue()
    
    def getValue(self, vlookup, index):
        return vlookup[index]
    
    def getValue2D(self, vlookup, index, x, y):
        return vlookup[x, y]  