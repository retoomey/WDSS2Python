"""
NetcdfReader class file

There are several different Netcdf libraries out there.  ArcGIS has some netcdf reading ability,
and there is Scientific Python among others.  We use this class as a wrapper to plug in different
libraries.  I've notice the way ArcGIS reads data is kinda slow for large files..maybe I have
more to learn about how to use it properly.

@author: Robert Toomey (retoomey)
"""

import os, gzip
import w2py.log as log
import w2py.resource as w2res

class netcdfReader(object):
    def __init__(self):
        self.haveTemp = False
        self.fileName = None
        
    def getFileLocation(self):
        """ Get the actual file location.  Can be the original file or a temporary uncompressed file """
        return self.fileName
    
    def setFileLocation(self, f):
        """ Set the file location used by this reader """
        self.fileName = f 
              
    def uncompressTempFile(self, datafile):
        """ Uncompress a gzip file to a temp file if needed """
        if datafile.endswith(".gz"):
            uncompressed = w2res.getAbsBaseMulti(datafile)
            uncompressed += ".netcdf"
            log.info("Uncompressing file to "+uncompressed)
            i = gzip.GzipFile(datafile, 'rb')
            fileData = i.read()
            i.close()
            o = file(uncompressed, 'wb')
            o.write(fileData)
            o.close()
            datafile = uncompressed
            self.setFileLocation(uncompressed)
            self.fileName = uncompressed
            self.haveTemp = True
            datafile = uncompressed
        else:
            self.setFileLocation(datafile)
        return datafile  
    

    def __del__(self):
        if self.haveTemp:
            log.info("Attempting to remove temp file"+self.fileName)
            os.remove(self.fileName)
         
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
