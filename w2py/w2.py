'''
The main script for accessing our datatypes

Read custom netcdf data files into ArcGIS using an ArcGIS toolbox python
script
Design the script to run from ArcGIS, or standalone using sys.args.
For now, do lots of work here.  Some of this will migrate/separate later

@author: Robert Toomey (retoomey)
'''

# System imports
import arcpy, os, shutil, time

# Local import (same folder)
import log
import w2py.resource as w2res
import w2py.html as w2html

# Library folder imports
from netcdf import netcdf_util
from w2py.datatype import datatype as datatype
from w2py.datatype.latlongrid import LatLonGrid

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

def genPNGFile(D, featureLocation, outHTMLFolder, outputPNGfile, asymboll=""):  
    """ Given one of our DataType objects, and a arcgis Feature file, output the feature as a PNG.
        Return the full path to new image file"""
        
    # For our HTML generation, we will use a temporary .mxd file to do the imaging work...
    # MapDocument doesn't allow creating a new blank document, so we 'copy' our 'blank.mxd' to 
    # a temp file and use that
    blanktemplate = w2res.getArcgisFilename("blank.mxd")
    work = w2res.getTempFile(outHTMLFolder, "working.mxd")
    workpng = w2res.getTempFile(outHTMLFolder, outputPNGfile)
    
    # Clean up any old working files
    if os.path.isfile(work):
        os.remove(work)
    if os.path.isfile(workpng):
        os.remove(workpng)   
        
    # Copy our template to a working copy...
    shutil.copyfile(blanktemplate, work)
    mxd = arcpy.mapping.MapDocument(work)
    dataFrame = arcpy.mapping.ListDataFrames(mxd)[0]
    
    # Add a map layer to the dataframe...FIXME: make optional or choosable
    # FIXME: check for existance
    usashp = w2res.getArcgisFilename("usa.shp")
    usaSymLayer = w2res.getArcgisFilename("usa.lyr")
    log.info("USA LAYER FILE IS "+str(usaSymLayer))
    usaLayer = arcpy.mapping.Layer(usashp)
    arcpy.ApplySymbologyFromLayer_management(usaLayer, usaSymLayer)
    arcpy.mapping.AddLayer(dataFrame, usaLayer, "TOP")
    ext = usaLayer.getExtent()
    
    # Add our Raster image to the dataframe, if we have one
    if D.haveRaster() == True:
        iwidth = D.getImageWidth()
        iheight = D.getImageHeight()
    
        rasterLyr = arcpy.mapping.Layer(featureLocation)

        # Apply symbology if we have it...
        if asymboll:
            log.info("SYMBOLOGY LAYER FILE IS "+str(asymboll))
            arcpy.ApplySymbologyFromLayer_management(rasterLyr, asymboll)
        else:
            log.info("No symbology layer given, leaving default symbology in PNG") 
        
        arcpy.mapping.AddLayer(dataFrame, rasterLyr, "TOP")
        ext = rasterLyr.getExtent()
           
    else:
        log.info("*****We don't have a raster of data....")
        # Output just a map for this file...
        iwidth = 500
        iheight = 200
    
    # Set the extent of the final output png.  We'll zoom to the  raster layer if possible,
    # or the map layer if possible
    dataFrame.extent = ext
    
    # Save the temp map and export to PNG  
    mxd.save()
    arcpy.mapping.ExportToPNG(mxd, workpng, dataFrame, iwidth, iheight, 300)
    log.info("Wrote png of arcgis map to "+workpng)
    
    # Clean up layers from memory and temp files
    del mxd, usaLayer
    if D.haveRaster() == True:
        del rasterLyr
    if os.path.isfile(work):
        os.remove(work)
    
    return workpng  

def writeArcPyRaster(llg, outputlocation):
    """ Write a arc python Raster given  LatLonGrid datatype.  For now,
        just keep this code here.  Eventually will create a separate arcpy library """ 
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
    #log.info("M is "+str(type(M)))
    #log.info("M shape is "+str(M.shape[0])+","+str(M.shape[1])+", "+str(dlon)+","+str(dlat))
    myRaster = arcpy.NumPyArrayToRaster(M, lowerLeft, dlon, dlat, datatype.missingData)
    arcpy.DefineProjection_management(myRaster, sr)
   
    log.info("Attempting to write raster to "+outputlocation)
    #When using raster.save your choices are Geodatabase Raster, Esri Grid, GeoTiff and ERDAS imagine format.
    myRaster.save(outputlocation)
    llg.setRaster(myRaster)
        
    return myRaster

def readSingleFileToRaster(datafile, output, net, htmlOn=False, symbols=None, hFolder=None):
    """ Given a file location and an output location, 
        try to read it using the netcdf reader
        Everything here wraps through our interface so it will work 
        with ArcToolbox or with console """
    
    log.setDefaultProgress("Reading a single file...")
    
    # Get the reader from our netcdf module and read the file
    # into our 'datatype' class.  Then output to arcpy feature
    reader = getReader(datafile, net)
    D = netcdf_util.readNetcdfFile(reader)
    if D != None:
        D.setFileName(datafile)
    
    # Current only LatLonGrids can output to raster...
    # Most likely RadialSets will become polygon shapefiles or tables...etc...
    # We will probably want a table injest function for radial sets..
    
    newFeature = None
    if isinstance(D, LatLonGrid):
        # Create a new Raster feature for our LatLonGrid datatype
        newFeature = writeArcPyRaster(D, output)
        
        # Generate an HTML page for this Datatype, including our PNG file
        if htmlOn:
            log.info("Generating PNG and HTML files to "+hFolder)
            
            # Get a generated output file names for HTML and PNG
            baseName = w2res.getBaseMulti(datafile)
            pngName = baseName+".png"
            htmlName = baseName+".html"
            
            # Generate an PNG file page for this Raster
            genPNGFile(D, output, hFolder, pngName, symbols)
            w2html.genHTMLFile(D, hFolder, htmlName, pngName)
        
    else:
        log.info(">>>>>>>>>>>>>>>Skipping generation for non LatLonGrid type.")
        log.info("The type is "+str(type(D)))
    

    log.resetProgress()
    return newFeature
          
def readMultipleFiles(inFolder, outFolder, net, htmlOn=False, symbols=None, hFolder=None):  
    """ Given a input folder and output folder, try to read
        every possible file in the tree, creating an equal converted
        file """
    
    # We'll create a geodatabase in the output folder to stick all features
    # in.  The way ArcToolbox parameters handles this stuff is really bad design.
    gdbpath = os.path.abspath(os.path.join(outFolder, "thedatafiles.gdb"))
    if not os.path.exists(gdbpath):
        arcpy.CreateFileGDB_management(outFolder, "thedatafiles.gdb")
    log.info("Using geodatabase at "+gdbpath)
    
    # Create the index.html file.  This will be a table of contents for the datafiles
    if htmlOn:
        indexLocation = os.path.join(hFolder, "index.html")
        outHTMLindex = os.path.abspath(indexLocation)
        outHTMLindex = open(outHTMLindex, "w")
        w2html.genHTMLHeader(outHTMLindex, "Table of Contents")
        outHTMLindex.write("This is a table of contents of all data files<br>\n<ul>\n")
        
    # First walk to gather all possible files and sort them
    # This could be a memory pig for large collections of files, but makes our index
    # and prev/next html link generation a lot easier..
    fileCount = 0
    filelist = []
    maxFiles = 10000  # Allow breaking out after a certain number of files...
    for dir, sub, files in os.walk(inFolder):
        for f in files:
            
            # Get the full path and see if it ends in a handled extension type (netcdf)
            absPath = os.path.abspath(os.path.join(dir, f))
            if w2res.isHandledFileType(absPath):
                fileCount += 1
                filelist.append(absPath)
                if fileCount >= maxFiles:
                    break
        if fileCount >= maxFiles: 
            break
    filelist.sort()
    log.info("File count size is "+str(len(filelist)))   
         
    # Now march each file and try to convert...
    # FIXME: How to check if user pressed Cancel button?            
    log.setStepProgress("Files", 0, fileCount, 1)
    #c = 1
    for c, f in enumerate(filelist):
        #for f in files:
        log.setProgressLabel("Handling {0}, file {1}/{2}".format(f, c+1, fileCount))
        #c += 1
 

        try:                
            # Get NetCDF reader for this file and get our DataType object
            reader = getReader(f, net)
            D = netcdf_util.readNetcdfFile(reader)
            if D != None:
                D.setFileName(f)
            log.info("Successfully read file "+f)
            
            if isinstance(D, LatLonGrid):
                
                # Make a safe base filename for HTML/PNG and Raster generation
                baseName = w2html.genFileBase(f)
                
                # We'll output the raster as a grid to the geodatabase we created,
                # replacing characters that confuse ArcGIS. Tried making other files
                # and had issues with rasters not coming out correct.
                output = os.path.abspath(os.path.join(gdbpath, baseName))
                log.info("Raster output location is "+output)
            
                # Create a new Raster feature for our LatLonGrid datatype
                # For now, only write a new one if it doesn't exist.  Eventually
                # should respect the overwrite environment
                ex = arcpy.Exists(output)
                if ex:
                    log.info("Raster already exists, reading from cache: "+output)
                    r =arcpy.Raster(output)
                    D.setRaster(r)   
                else:
                    writeArcPyRaster(D, output)
                
                # Generate an HTML page for this Datatype, including our PNG file
                if htmlOn:
                    log.info("Generating PNG and HTML files to "+hFolder)
                
                    # Get a generated output file names for HTML and PNG
                    pngName = baseName+".png"
                    htmlName = baseName+".html"
                    
                    # Generate navigation links that cycle...
                    # prev page in our HTML file collection
                    if (c - 1) >= 0:
                        prevFile = w2html.genFileBase(filelist[c-1])
                    else:
                        prevFile = w2html.genFileBase(filelist[len(filelist)-1])
                         
                    # next page in our HTML file collection
                    if (c + 1) < len(filelist):
                        nextFile = w2html.genFileBase(filelist[c+1])
                    else:
                        nextFile = w2html.genFileBase(filelist[0])
                        
                    # Generate an PNG file page for this Raster
                    genPNGFile(D, output, hFolder, pngName, symbols)
                    w2html.genHTMLFile(D, hFolder, htmlName, pngName, "index.html",
                                       prevFile, nextFile)
                    
                    shortName = os.path.basename(f)
                    w2html.genHTMLListItem(outHTMLindex, htmlName, shortName)
                
                # Delete the netcdf and raster files to keep ArcGIS memory getting too big
                del D
            else:
                log.info(">>>>>>>>>>>>>>>Skipping generation for non LatLonGrid type.")
                log.info("The type is "+str(type(D)))
            
            del reader
                
        # Normally not good to catch all exceptions, but we want to keep going when
        # there's a big batch job, so we'll allow it here, but show the reason for the error.
        except Exception as e:
            log.error("Got exception parsing file "+absPath)
            log.error("Error is "+str(e.args))
            
        log.setProgressPosition()
        time.sleep(0.5)      
    log.resetProgress()
    
    if htmlOn:
        outHTMLindex.write("</ul>\n")
        w2html.genHTMLFooter(outHTMLindex)
