"""
LatLonGrid

Data object to hold our raster data type

@author: Robert Toomey (retoomey)
""" 
 
import datatype

class LatLonGrid(datatype.DataType):
    def __init__(self, M, lat, lon, dlat, dlon):
        """ Hold the stuff for a lat lon grid.  This is a raster
            data type.
            M: 2D numpy matrix of the grid (X is lon, Y is lat)
            lat: Latitude in degrees upper left
            lon: Longitude in degrees upper left
            dlat: Lat cell size in degrees
            dlon: Lon cell size in degrees
        """
        datatype.DataType.__init__(self)
        self.matrix = M
        self.lat = lat
        self.lon = lon
        self.dlat = dlat
        self.dlon = dlon
    
    def __del__(self):
        """ Delete the numpy array to save memory.   """
        datatype.DataType.__del__(self)
        del self.matrix
           
    def getUpperLeft(self):
        return [self.lon, self.lat]
    
    def getLowerLeft(self):
        return [self.lon, self.lat-(self.dlat*self.matrix.shape[0])]
    
    def getValues(self):
        return self.matrix
    
    def getLat(self):
        return self.lat
    
    def getLon(self):
        return self.lon
    
    def getCellSizeX(self):
        return self.dlon
    
    def getCellSizeY(self):
        return self.dlat
    
    def getCellSize(self):
        return [self.dlon,self.dlat]
    
    def getImageWidth(self):
        """ Return the image width for this data type 
            (used in HTML and PNG generation) """
        return self.matrix.shape[1]
    
    def getImageHeight(self):
        """ Return the image height for this data type 
            (used in HTML and PNG generation) """
        return self.matrix.shape[0]
