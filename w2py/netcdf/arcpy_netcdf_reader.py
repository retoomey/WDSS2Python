"""
Arcpy Netcdf Reader class file

This reader uses the arcpy NetCDFFileProperties to access a netcdf file

@author: Robert Toomey (retoomey)
""" 

import arcpy
from w2py import log 

import netcdf_reader

class arcpyNetcdfReader(netcdf_reader.netcdfReader):
    
    def __init__(self, datafile):
        """ Open NetCDF file with arcpy library
        """
        log.info("Trying to read netcdf "+datafile)
        try:
            self.data  = arcpy.NetCDFFileProperties(datafile)
        except BaseException as e:
            log.error("Couldn't read netcdf data from file "+datafile)
            log.error("Exception {0}".format(e))
    
    def haveDimension(self, dim):
        """ Read in first element of a netcdf dimension...if there's an exception return False.
        We have some optional dimension data, this makes the code cleaner
        """
        haveIt = False
        try:
            self.data.getDimensionValue(dim, 0)
            haveIt = True
        except:
            # Assume it's not there...
            pass
        return haveIt
    
    def haveAttribute(self, param1, param2):
        attrs = self.data.getAttributeNames(param1)
        return param2 in attrs
    
    def getAttributeValue(self, param1, param2):
        return self.data.getAttributeValue(param1, param2)
    
    def getDimensionSize(self, param1):
        return self.data.getDimensionSize(param1)
    
    def getDimensionSizeByVariable(self, param1):
        dims = self.data.getDimensionsByVariable(param1)
        num = self.data.getDimensionSize(dims[0])
        return num  

    def getValueLookup(self, param1):
        # In arcpy just have a keyname
        return param1
    
    # Slower than a snail in arcgis..they wrap an object every call.
    # really? lol
    def getValue(self, vlookup, index):
        return self.data.getDimensionValue(vlookup, index)
    
    def getValue2D(self, vlookup, index, x, y):
        return self.data.getDimensionValue(vlookup, index)
        