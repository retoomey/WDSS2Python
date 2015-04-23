# Robert Toomey (retoomey)
# The main library for accessing our datatypes
#
# Read custom netcdf data files into ArcGIS using an ArcGIS toolbox python script
# Design the script to run from ArcGIS, or standalone using sys.args.

import arcpy, os
import log
from netcdf import netcdf_util
from w2py.datatype import datatype as datatype
from w2py.datatype.latlongrid import LatLonGrid
import shutil

def getReader(datafile, net):  
    """ Get the netcdf reader we will use to injest our data"""
    from netcdf import arcpy_netcdf_reader
    from netcdf import sci_netcdf_reader
    
    # Running in ArcGIS it doesn't reload python..this is for debuggng:
    if (log.debug):
        reload(arcpy_netcdf_reader)
        reload(sci_netcdf_reader)
        
    if ("SCIENTIFIC" in net):
        log.info("Using SCIENTIFIC python netcdf parser")
        return sci_netcdf_reader.sciNetcdfReader(datafile)
    else:
        log.info("Using ArcGIS netcdf parser (slow)")
        # Using ArcGIS NetCD.  So slow..so very, very slow
        return arcpy_netcdf_reader.arcpyNetcdfReader(datafile)

def generateHTMLPage(llg, myRaster, outputlocation):  
    
    M = llg.getValues()
    # For our HTML generation, we will use a temporary .mxd file to do the imaging work...
    # MapDocument doesn't allow creating a new blank document, so we 'copy' our 'blank.mxd' to 
    # a temp scratch file and use that...
    # FIXME: pick some safe path and filename...
    blanktemplate = "C:/Temp22/blank.mxd"
    work = "C:/Temp22/working.mxd"
    workpng = "C:/Temp22/testing1.png"
    
    asymboll = "C:/PData/cloudcover.lyr"
    tempLyr = "C:/Temp22/goopers.lyr"
    
    usamapl = "C:/Temp22/usa.lyr"
    tempLyr2 = "C:/Temp22/goopers2.lyr"
    
    # Clean up any old working files
    if os.path.isfile(tempLyr):
        os.remove(tempLyr)
    if os.path.isfile(tempLyr2):
        os.remove(tempLyr2)
    if os.path.isfile(work):
        os.remove(work)
    if os.path.isfile(workpng):
        os.remove(workpng)   
        
    # Copy our template to a working copy...
    shutil.copyfile(blanktemplate, work)
    mxd = arcpy.mapping.MapDocument(work)
    dataFrame = arcpy.mapping.ListDataFrames(mxd)[0]
    
    # Add a map layer to the dataframe...
    shutil.copyfile(usamapl, tempLyr2)
    lyr2 = arcpy.mapping.Layer(tempLyr2)
    arcpy.mapping.AddLayer(dataFrame, lyr2, "TOP")
    
    # From the raster file, create a new layer...
    arcpy.MakeRasterLayer_management(outputlocation, "rdlayer")
    arcpy.SaveToLayerFile_management("rdlayer", tempLyr)
    lyr = arcpy.mapping.Layer(tempLyr)
       
    #Try to apply symbology
    arcpy.ApplySymbologyFromLayer_management(lyr, asymboll)
    arcpy.mapping.AddLayer(dataFrame, lyr, "TOP")
    
    # Set the data frame extent to match the LatLonGrid exactly.  This way the PNG is just the area
    # of our raster.  If we add a USA map, maybe we should expand this some....
    ext = myRaster.extent
    dataFrame.extent = ext
    
    log.info("Extent is "+str(ext))
    mxd.save()
    
    res = 300

    arcpy.mapping.ExportToPNG(mxd, workpng, dataFrame, M.shape[1], M.shape[0], res)
 
    #mxd.saveACopy("adfsadfasdf")
    del mxd, lyr, lyr2
         
def writeArcPyRaster(llg, outputlocation):
    """ Write a arc python Raster given  LatLonGrid datatype """ 
    # Our lat/lon give the top right..arcgis wants in bottom left...
    # This map works for the USA CONUS, might need work for other areas of world
    # Move the lat to bottom left corner.     
    M = llg.getValues()

    dlat = llg.getCellSizeX()
    dlon = llg.getCellSizeY()

    ll = llg.getLowerLeft()
    log.info("Lowerleft is "+str(ll))
    lowerLeft = arcpy.Point(ll[0], ll[1])
    
    sr = arcpy.SpatialReference(4326) # WGS 1984
    myRaster = arcpy.NumPyArrayToRaster(M, lowerLeft, dlon, dlat, datatype.missingData)
    arcpy.DefineProjection_management(myRaster, sr)
   
    log.info("Attempting to write raster to "+outputlocation)
    #When using raster.save your choices are Geodatabase Raster, Esri Grid, GeoTiff and ERDAS imagine format.
    myRaster.save(outputlocation)
    log.info("Wrote raster to "+outputlocation)
    
    generateHTMLPage(llg, myRaster, outputlocation)
    
    return myRaster

def readSingleFileToRaster(datafile, output, net):
    """ Given a file location and an output location, 
        try to read it using the netcdf reader
        Everything here wraps through our interface so it will work 
        with ArcToolbox or with console """
    
    log.setDefaultProgress("Reading a single file...")
    log.info("Datafile is "+datafile)
    log.info("Output is "+output)
    log.info("Netcdf reader is "+net)
    
    # Get the reader from our netcdf module and read the file
    # into our 'datatype' class.  Then output to arcpy feature
    reader = getReader(datafile, net)
    D = netcdf_util.readNetcdfFile(reader)
    
    # Current only LatLonGrids can output to raster...
    # Most likely RadialSets will become polygon shapefiles or tables...etc...
    # We will probably want a table injest function for radial sets..
    newFeature = None
    if isinstance(D, LatLonGrid):
        newFeature = writeArcPyRaster(D, output)
    else:
        log.info(">>>>>>>>>>>>>>>Skipping raster generation for non LatLonGrid type.")
    
    log.resetProgress()
    return newFeature
          
def readMultipleFiles(inFolder, outFolder, net):    
    """ Given a input folder and output folder, try to read
        every possible file in the tree, creating an equal converted
        file """
        
    # First walk to count all possible files...
    # This is just a guess since files could be added/removed from the tree
    # before the next call. I haven't figured out a better way to do this...
    # Could store the walk and then use that, but that could be a memory pig
    fileCount = 0
    for dir, sub, files in os.walk(inFolder):
        for f in files:
            fileCount += 1
    log.setStepProgress("Files", 0, fileCount, 1)
    
    # Now march each file and try to convert...
    c = 1
    for dir, sub, files in os.walk(inFolder):
        for f in files:
            log.setProgressLabel("Handling {0}, file {1}/{2}".format(f, c, fileCount))
            c += 1
            log.setProgressPosition()
            try:
                reader = getReader(f, net)
                D = netcdf_util.readNetcdfFile(reader)
                log.info("Read file "+f)
            except:
                log.error("Got exception reading "+f)
                  
    log.resetProgress()

def readFromCommandLine(parameters, messages):
    datafile = 'C:\GIS-GRADSCHOOL\GIS540-SP2015\Project\polartest.netcdf'
    datafile = 'C:\GIS-GRADSCHOOL\GIS540-SP2015\Project\LatLonGrid20150401-204712.netcdf'
    output = 'C:\GIS-GRADSCHOOL\GIS540-SP2015\Project\polartestout'
    
    reader = getReader(datafile)
    netcdf_util.readNetcdfFile(reader, output)
    
