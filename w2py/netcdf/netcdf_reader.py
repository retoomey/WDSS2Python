"""
NetcdfReader class file

There are several different Netcdf libraries out there.  ArcGIS has some netcdf reading ability,
and there is Scientific Python among others.  We use this class as a wrapper to plug in different
libraries.  I've notice the way ArcGIS reads data is kinda slow for large files..maybe I have
more to learn about how to use it properly.

@author: Robert Toomey (retoomey)
"""

class netcdfReader(object):
    def haveDimension(self, dim):
        return False
    def haveAttribute(self, param1, param2):
        return False
    #def getAttributeNames(self, params):
    #    return None
    def getAttributeValue(self, param1, param2):
        return None
    def getDimensionSize(self, param1):
        return None
    def getDimensionSizeByVariable(self, param1):
        return None
    def getValueLookup(self, param1):
        return None
    def getValue(self, vlookup, index):
        return None
    def getValue2D(self, vlookup, index, x, y):
        return None
