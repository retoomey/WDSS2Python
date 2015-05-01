"""
Netcdf utilities

Basically, read NSSL netcdf data. Lots of boring stuff here.  The main points are:
    1. Finding our special NetCDF attributes and variables
    3. Reading a NSSL Polar Radial Dataset
       OR reading a NSSL LatLonGrid Dataset
    2. Handling our custom sparse data storage

@author: Robert Toomey (retoomey)
"""

# We use numpy for matrix data storage
import numpy, datetime

from w2py import log
from w2py.datatype import datatype as datatype
from w2py.datatype import radialset
from w2py.datatype import latlongrid
   
def getDimension(data, dim):
    """ Read in first element of a netcdf dimension...if there's an exception return False.
        We have some optional dimension data, this makes the code cleaner
    """
    haveIt = False
    try:
        data.getDimensionValue(dim, 0)
        haveIt = True
    except:
        # Assume it's not there...
        pass
    return haveIt

# FIXME: Probably break up into classes eventually....
def readRadialSet(data, isSparse):
    """ Try to read in a NSSL RadialSet data format.
    """
    # Get the radar elevation in degrees
    e = data.getAttributeValue("", "Elevation")
    elevation = float(e)
    log.info("Radar elevation angle: {0} degrees.".format(elevation))

    # Get distance to first gate in meters
    d = data.getAttributeValue("", "RangeToFirstGate")
    distToFirstGate = float(d)
    log.info("Distance to first gate: {0} meters.".format(distToFirstGate))
    
    # Read the main data of the file into 2D array
    datatype = data.getAttributeValue("", "TypeName")
    # Assume Sparse
    M = None
    if isSparse:
        log.info("Data type is SPARSE")
        M = readSparseArray2Dfloat(data, datatype, "Azimuth", "Gate")
    else:
        log.info("Data is not SPARSE")
        M = readArray2Dfloat(data, datatype, "Azimuth", "Gate")
     
    # Ok, now create the radial set
 
    if M != None:
        log.info("X size is "+str(M.shape[0]))
        log.info("Y size is "+str(M.shape[1]))  
        num_radials = M.shape[0]
        
        # Get out 'lookups'  keys that depend on the library we're using
        # they are used to access data at an index
        haveAs = getDimension(data, "AzimuthalSpacing")
        haveNy = getDimension(data, "NyquistVelocity")
        azimuthL = data.getValueLookup("Azimuth")
        beamwidthL = data.getValueLookup("BeamWidth")
        if haveAs:
            azimuthalSpacingL = data.getValueLookup("AzimuthalSpacing")
        if haveNy:
            nvl = data.getValueLookup("NyquistVelocity")
        gatewidthL = data.getValueLookup("GateWidth")
        nyquest = -99999.0
        
        for i in range(0,num_radials):
            az = float(data.getValue(azimuthL, i))
            bw = float(data.getValue(beamwidthL, i))
            if haveAs:
                aspace = float(data.getValue(azimuthalSpacingL, i))
            else:
                aspace = bw  # Spacing is equal to beamwidth
            if haveNy:
                ny = float(data.getValue(nvl, i))
            else:
                ny = nyquest
            gw = int(data.getValue(gatewidthL, i)) 
               
            log.info("{0}, {1}, {2}, {3}, {4}".format(az,bw,aspace, ny,gw))
        
        rs = radialset.RadialSet(M)
        rs.setTypeName(datatype)   
        return rs
    else:
        log.error("Could not find DataType attribute in Netcdf file.  All NSSL netcdf data files should have this.")
    return None

def readLatLonGrid(data, isSparse):
    """ Try to read in a NSSL LatLonGrid data format
    """    
    log.debug("Entering readLatLonGrid")
    lat = float(data.getAttributeValue("", "Latitude"))
    lon = float(data.getAttributeValue("", "Longitude"))
    dlat = float(data.getAttributeValue("", "LatGridSpacing"))
    dlon = float(data.getAttributeValue("", "LonGridSpacing"))
    
    # Read the main data of the file into 2D array
    datatype = data.getAttributeValue("", "TypeName")
    # Assume Sparse
    M = None
    if isSparse:
        log.info("Data type is SPARSE")
        M = readSparseArray2Dfloat(data, datatype, "Lat", "Lon")
    else:
        log.info("Data is not SPARSE")
        M = readArray2Dfloat(data, datatype, "Lat", "Lon")
    
    llg = latlongrid.LatLonGrid(M, lat, lon, dlat, dlon)
    llg.setTypeName(datatype)
    return llg
    
def readNetcdfFile(data): 
    """ Read in a netcdf data file, look for our attributes.
        Using Arcpy's built in netcdf ability.  This of course relies on the arcpy
        library.  Could wrap all the netcdf to allow plug-in of SciPy or another library
    """  
    D = None  
    if data.haveAttribute("", "DataType"):
        
        #dataType = attrs.get("DataType")
        dataType = data.getAttributeValue("", "DataType")
        log.info("DataType is "+dataType)
          
        # Get the origin of the data. 
        lat = float(data.getAttributeValue("", "Latitude"))
        lon = float(data.getAttributeValue("", "Longitude"))
        h = float(data.getAttributeValue("", "Height"))
        log.info("Data origin: {0}, {1}, {2} Meters".format(lat,lon,h))
         
        # First attempt, assume RadialSet...
        # We'll have to dispatch for RadialSet/LatLonGrid
        isSparse = "Sparse" in dataType
        if "RadialSet" in dataType:
            D = readRadialSet(data, isSparse)
        elif "LatLonGrid" in dataType:
            D = readLatLonGrid(data, isSparse)
        else:
            log.error("Can't process unknown DataType of "+dataType)
            
        # Try to get the time from the data file...
        if data.haveAttribute("", "Time"):
            t1 = long(data.getAttributeValue("", "Time"))
            #t2 = float(0.0)
            #if data.haveAttribute("", "FractionalTime"):
            #   t2 = float(data.getAttributeValue("", "FractionalTime"))
            #log.info("************************T1 is "+str(t1))
            #log.info("************************T2 is "+str(t2))
            #t1 = t1 + long(1000.0*t2)
            theTime = datetime.datetime.fromtimestamp(t1).strftime('%Y-%m-%d %H:%M:%S UTC')
        else:
            # We don't care, just use current date...           
            theTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC') 
            
        D.setTime(theTime)
        
    else:
        log.error("No DataType attribute found in NetCDF file.")
    return D
  
def readArray2Dfloat(data, typename, rfield, cfield):
    """ Read in a non 2D array from our netcdf data and expand. 
        For the initial project, we will just handle sparse data.
    """    
    #log.info("NUMPY version is {0}".format(numpy.version.version))

    rows = data.getDimensionSize(rfield)
    cols = data.getDimensionSize(cfield)
    # Humm..need this index I think.  Don't know how to use it properly
    #index = data.getDimensionIndex(typename)
    
    #log.info("Filling in data values "+str(rows)+","+str(cols))
    M = numpy.empty((rows,cols), float)
    i = 0
    notify = 0
    totalCells = 0
    allCells = rows*cols
    log.info("Type name comes in as "+typename)
    values = data.getValueLookup(typename)
    log.info("Type name of values is "+str(type(values)))
    for x in range(0,rows):
        for y in range(0, cols):
            M[x,y] = float(data.getValue2D(values, i, x, y))
            i = i + 1
            notify += 1
            totalCells += 1
            if notify > 10000:
                log.info("Processed {0} of {1} data samples.".format(totalCells, allCells))
                notify = 0
    log.info("Processed {0} of {1} data samples.".format(totalCells, allCells))
    return M

def readSparseArray2Dfloat(data, typename, rfield, cfield):  
    """ Read in a sparse 2D array from our netcdf data and expand. 
    """    
    backgroundValue = float(data.getAttributeValue(typename, "BackgroundValue"))
    log.info("Background value is "+str(backgroundValue))
    
    num_pixels = data.getDimensionSizeByVariable("pixel_x")
    
    # Try to get the count field, if any.  This will cause an exception if missing.  This is
    # an extra line based compression, since radar data tends to be locally homogeneous
    haveCount = False
    try:
        count = data.getDimensionSizeByVariable("pixel_count")
        haveCount = True
    except Exception as e:
        # Assume it's not there...
        pass
    
    #log.info("NUMPY version is {0}".format(numpy.version.version))

    # Bleh, Arcgis 10.2 has numpy 1.7, so we can't fill with background value automatically
    rows = data.getDimensionSize(rfield)
    cols = data.getDimensionSize(cfield)
    log.info("Creating background array of {0}, {1}".format(rows, cols))
    M = numpy.empty((rows,cols), float)
    for x in range(0,rows):
        for y in range(0,cols):
            M[x,y] = backgroundValue
    
    # Basically, for sparse array.  We have an 'x' and 'y' that tell position into the array, and
    # a possible 'pixel_count' which is a line of same data value.
    #log.info("Filling in data values")
    actualData = 0
    notify = 0
    totalCells = 0
    pixelL = data.getValueLookup(typename)
    pixel_xL = data.getValueLookup("pixel_x")
    pixel_yL = data.getValueLookup("pixel_y")
    if haveCount:
        pixel_countL = data.getValueLookup("pixel_count")
    
    for i in range(0, num_pixels,1):

        # Data value and the sparse x, y location in full matrix
        value = float(data.getValue(pixelL, i))
        x = int(data.getValue(pixel_xL, i))
        y = int(data.getValue(pixel_yL, i))
        
        # Each can be a line strip of values at the location
        if haveCount:
            count = int(data.getValue(pixel_countL, i))
        else:
            count = 1
        #log.info("**************Count is "+str(haveCount))    
        if value > datatype.missingData:
            M[x, y] = value
            actualData += 1
        totalCells += 1
        notify += 1
        
        if notify > 10000:
                log.info("Processed {0} of {1} data samples.".format(totalCells, num_pixels))
                notify = 0
        # Fill in line strip
        for j in range(1, count, 1):
            y += 1
            if y == cols:
                x += 1   # new row
                y = 0
            if value > datatype.missingData:
                M[x, y] = value
                actualData += 1  
            #print x, y, count, "set to", value
    log.info("Processed {0} of {1} data samples.".format(totalCells, num_pixels))
    return M
