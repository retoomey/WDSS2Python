"""
RadialSet

Data object to hold our polar radar set data

@author: Robert Toomey (retoomey)
"""  
 
import datatype

class RadialSet(datatype.DataType):
    def __init__(self, M):
        """ Hold the stuff for a polar radial set
        """
        datatype.DataType.__init__(self)
        self.matrix = M
        