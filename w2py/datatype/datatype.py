"""
Datatype

Data object to hold our base data type for all WDSS2 products

@author: Robert Toomey (retoomey)
"""   
missingData = -99900.0
rangeFolded = -99901.0
dataUnavailable = -99903.0

class DataType(object):
    def __init__(self):
        """ Create a datatype, the root class of all our data classes """
        self.raster = None
        self.hRaster = False
        self.time = None
        self.typeName = "Unknown"
        self.fileName = "Unknown Filename"
    
    def __del__(self): 
        """ Delete the raster to save memory """
        if self.hRaster:
            del self.raster
        
    def getRaster(self):
        """ Get an optional arcpy raster """
        return self.raster
    
    def setRaster(self, raster):
        """ Set an optional arcpy raster """
        self.raster = raster
        self.hRaster = True
        
    def haveRaster(self):
        """ Do we have a raster object? """
        return self.hRaster
    
    def getImageWidth(self):
        """ Return the image width for this data type 
            (used in HTML and PNG generation) """
        return 500
    
    def getImageHeight(self):
        """ Return the image height for this data type 
            (used in HTML and PNG generation) """
        return 200
    
    def setTime(self, t):
        self.time = t
    
    def getTime(self):
        return self.time

    def setTypeName(self, n):
        self.typeName = n
    
    def getTypeName(self):
        return self.typeName
    
    def setFileName(self, f):
        self.fileName = f
    
    def getFileName(self):
        return self.fileName