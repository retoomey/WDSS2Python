# Robert Toomey
# ArcGIS Python Toolbox for importing custom WDSSII data format into ArcGIS
# We'll try to keep just GUI code here and do all the work in our python command line code

# March/April 2015

import arcpy, sys, os
import w2py.w2, w2py.log
           
class Toolbox(object):
    def __init__(self):
        """ Initialize a ArcGIS Python Toolbox """
        #linkCustomPythonLibrary()
        self.label =  "WDSSII toolbox"
        self.alias  = "wdssii"
           
        # List of tool classes associated with this toolbox
        # Would be nice to be able to hide these in individual files
        # eventually
        self.tools = [ImportW2NetcdfRaster, MImportW2NetcdfRaster] 

#########################################################################################
### Define some shared toolbox parameters that can be used for multiple tools
###
def reloadModules():
    # We reload our worker script, because refreshing the ArcGIS toolbox doesn't
    # refresh any imported scripts.  And for speed testing in ArcGIS I want it to refresh
    # http://resources.arcgis.com/en/help/main/10.1/index.html#//001500000038000000
    reload(w2py.w2)
    reload(w2py.log)
    reload(w2py.netcdf.netcdf_util) 
    
def netcdfReaderChoice():
    """ Get the netcdf reader choice drop down menu parameter"""
    use_netcdf = arcpy.Parameter(
        displayName="Which netcdf library to use?",
        name="netcdf",
        datatype="String",
        parameterType="Optional",
        direction="Input")
    use_netcdf.filter.list = ["SCIENTIFIC", \
                              "ARCGIS"]
    use_netcdf.value = use_netcdf.filter.list[0]
    return use_netcdf

def netcdfFileChoice(multi):
    """ Get the file choice and filters for our netcdf data"""
    name = "Input WDSSII Netcdf file"
    if multi:
        name += "s"
     
    in_features = arcpy.Parameter(
        displayName=name,
        name="in_netcdf_file",
        datatype="DEFile",
        parameterType="Required",
        multiValue=multi,
        direction="Input")
    in_features.filter.list = ["netcdf", "nc"]
    return in_features

def folderChoice(isOutput, aName):
    """ Get input or output folder """
    if isOutput:
        aLabel = "Output folder"
        aType = "Output"
    else:
        aLabel = "Input folder"
        aType = "Input"
        
    folder = arcpy.Parameter(
        displayName=aLabel,
        name=aName,
        datatype="DEFolder",
        parameterType="Required",
        direction=aType) 
    
    return folder

def symbologyLayer():
    param0 = arcpy.Parameter(
        displayName="Input Feature Set",
        name="in_feature_set",
        datatype="GPFeatureRecordSetLayer",
        parameterType="Required",
        direction="Input")
    param0.value="C:/PData/cloudlayer.lyr"
    return param0

#########################################################################################
### Define all of our tools:
###  
class ImportW2NetcdfRaster(object):
    """ Tool for importing a single file from netcdf to raster """
    def __init__(self):
        self.label       = "W2 Netcdf to Raster"
        self.description = "Converts a National Severe Storms Laboratory data file, \
        in WDSSII Netcdf format to a raster dataset.  Current supports the NSSL LatLonGrid datatype."
           
    def getParameterInfo(self):
        """ Define toolbox parameters that will show in GUI """

        # Need one required for user to pick the destination
        out_features = arcpy.Parameter(
            displayName="Output raster",
            name="out_feature",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output")
        out_features.symbology="C:/PData/cloudcover.lyr"
        
        # One one that is derived so that results will autoload
        # Not sure why I'm having to duplicate this.  The ArcGIS help is
        # really lacking IMHO.  It might be because we aren't starting with any
        # ArcGIS recoqnized data type...
        out_d = arcpy.Parameter(
            displayName="Outputd",
            name="out_d",
            datatype="DERasterDataset",
            parameterType="Derived",
            direction="Output")
        
        p = [netcdfFileChoice(False), out_features, netcdfReaderChoice(), out_d]
        return p

    def isLicensed(self): #optional
        return True

    def updateParameters(self, parameters): #optional   
        return

    def updateMessages(self, parameters): #optional
        return

    def execute(self, p, messages):
        # Force reload and make our logger use ArcGIS feedback
        reloadModules()
        w2py.log.useArcLogging(messages, arcpy)
        
        # Read a single file using our library
        inDataFile = p[0].valueAsText
        outLocation = p[1].valueAsText
        netcdfType = p[2].valueAsText
        output = w2py.w2.readSingleFileToRaster(inDataFile, outLocation, netcdfType)
        
        # Assign output and we're done
        #p[1].symbology = "C:/PData/cloudcover.lyr"
        #p[3].symbology = "C:/PData/cloudcover.lyr"
        p[3].value = output
        
        
class MImportW2NetcdfRaster(object):
    """ Tool for importing multiple files from netcdf to raster """
    def __init__(self):
        self.label       = "W2 Netcdf to Raster (multiple)"
        self.description = "Converts multiple National Severe Storms Laboratory data file(s), \
        in WDSSII Netcdf format to raster dataset(s).  Current supports the NSSL LatLonGrid datatype."
           
    def getParameterInfo(self):
        
        p = [folderChoice(False, "Input"), folderChoice(True, "Output"), \
                      netcdfReaderChoice()]
        self.pdict = {"INPUT": p[0], "OUTPUT": p[1], "NETCDF": p[2]}
        return p

    def isLicensed(self): #optional
        return True

    def updateParameters(self, parameters): #optional
        return

    def updateMessages(self, parameters): #optional
        return

    def execute(self, p, messages):
        # Force reload and make our logger use ArcGIS feedback
        reloadModules()
        w2py.log.useArcLogging(messages, arcpy)
        
        # Read a directory tree using our library
        inFolder = p[0].valueAsText
        outFolder = p[1].valueAsText
        netcdfType = p[2].valueAsText
        w2py.w2.readMultipleFiles(inFolder, outFolder, netcdfType)
        #p[2].value = output

        
