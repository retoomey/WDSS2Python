# Robert Toomey (retoomey)
# Read custom netcdf data files into ArcGIS using an ArcGIS toolbox python script
# Design the script to run from ArcGIS, or standalone using sys.args.

import arcpy
import log

# Our netcdf wrapper, so we can swap out ArcGIS netcdf and Scientific python
from netcdf import arcpy_netcdf_reader
from netcdf import sci_netcdf_reader
from netcdf import netcdf_util

# ArcGIS messages when called from ToolBox
arcpy.env.overwriteOutput = True
       
def pointtest(output):
    global finalOutput
    
    poly = arcpy.Polygon()
    #Goop.  Create a point with each azvalue (totally wrong)
    ptList =[[20.000,43.000],[25.500, 45.085],[26.574, 46.025]]
    pt = arcpy.Point()
    ptGeoms = []
    for p in ptList:
        pt.x = p[0]
        pt.Y = p[1]
        ptGeoms.append(arcpy.PointGeometry(pt))

    arcpy.CopyFeatures_management(ptGeoms, output)
    finalOutput = output
        
# Called by the ArcGIS toolbox script, we pass onto our
# more generic function
def readFromArcGIS(parameters, messages):
    global finalOutput
    log.useArcLogging(messages)
    
    # Get parameters, pass to the code...
    datafile = parameters[0].valueAsText
    output = parameters[1].valueAsText

    log.info("Datafile is "+datafile)
    log.info("Output is "+output)
    #netcdf.readNetcdf(datafile, output)
    parameters[1].value = finalOutput
    
def readFromCommandLine(parameters, messages):
    datafile = 'C:\GIS-GRADSCHOOL\GIS540-SP2015\Project\polartest.netcdf'
    datafile = 'C:\GIS-GRADSCHOOL\GIS540-SP2015\Project\LatLonGrid20150401-204712.netcdf'
    output = 'C:\GIS-GRADSCHOOL\GIS540-SP2015\Project\polartestout'
    #netcdf.readNetcdf(datafile, output)
    #netcdf.readNetcdf(datafile, output)
    #netcdf.readNetcdf(datafile, output)
    
    # Using ArcGIS NetCDF.  So slow..so very, very slow
    #reader = arcpy_netcdf_reader.arcpyNetcdfReader(datafile)
    #netcdf_util.readNetcdfArcpy(reader, output)
    reader = sci_netcdf_reader.sciNetcdfReader(datafile)
    netcdf_util.readNetcdfArcpy(reader, output)
    
