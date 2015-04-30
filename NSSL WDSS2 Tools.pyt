# Robert Toomey
# ArcGIS Python Toolbox for importing custom WDSSII data format into ArcGIS
# We'll try to keep just GUI code here and do all the work in our python command line code

# March/April 2015

import arcpy, sys, os
import w2py.w2, w2py.log, w2py.resource
import w2py.resource as w2res
    
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
    # In a final non-changing release, could remove this code
    reload(w2py.w2)
    reload(w2py.log)
    reload(w2py.resource)
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
    in_features.filter.list = w2py.resource.getHandledFileTypes()
    
    # Some defaults using provided data files for testing.  User can change these
    if not multi:
        in_features.value = w2py.resource.getDataFilename("LatLonGrid20150401-204712.netcdf")

    return in_features

def folderChoice(isOutput, aName, aLabel, required=True):
    """ Get input or output folder """
    if isOutput:
        aType = "Output"
    else:
        aType = "Input"
    if required:
        r = "Required"
    else:
        r = "Optional"
          
    folder = arcpy.Parameter(
        displayName=aLabel,
        name=aName,
        datatype="DEFolder",
        parameterType=r,
        direction=aType) 
    
    return folder

def symbologyChoice():
    s = arcpy.Parameter(
        displayName="LatLonGrid symbology layer",
        name="in_lLG_symbology",
        datatype="DELayer",
        parameterType="Optional",
        direction="Input")
    
    # Default should be the tool file location...
    s.value = w2py.resource.getSymbologyLayer()
    return s

def generateHtmlChoice(flag):
    p = arcpy.Parameter(
        displayName="Generate HTML pages",
        name="make_html",
        datatype="Boolean",
        parameterType="Optional",
        direction="Input")
    p.value=flag
    return p

#########################################################################################
### Define all of our tools:
###  
class ImportW2NetcdfRaster(object):
    """ Tool for importing a single file from netcdf to raster """
    def __init__(self):
        self.label       = "W2 Netcdf to Raster"
        self.description = "Converts a National Severe Storms Laboratory data file, \
        in WDSSII Netcdf format to a raster dataset.  Current supports the NSSL LatLonGrid datatype."
        
        # Define a lookup map for our parameters.  This should match the 
        # creation of parameters in getParameterInfo.  We do this to avoid keeping
        # track of the index value changes (which prevents bugs).
        self.l = {"file":0, "out":1, "net":2, "html":3, "hFolder":4, "lyr":5 ,"dev":6}

    def getParameterInfo(self):
        """ Define toolbox parameters that will show in GUI """

        # Need one required for user to pick the destination
        out_features = arcpy.Parameter(
            displayName="Output raster",
            name="out_feature",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output")
        #out_features.symbology="C:/PData/cloudcover.lyr"
        
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
        htmlFolder = folderChoice(False, "html_output", "Output HTML/PNG Folder", False)
        htmlFolder.value = w2py.resource.getHTMLGenDir()
        
        # Create parameters. Match the list order to our self.l dictionary above
        p = [netcdfFileChoice(False), out_features, netcdfReaderChoice(),\
            generateHtmlChoice(False), htmlFolder, symbologyChoice(), out_d]
        return p

    def isLicensed(self): #optional
        return True

    def updateParameters(self, p): #optional 
        # Only require the html folder and settings if the Generate HTML button is on
        htmlOn = p[self.l["html"]].value
        p[self.l["lyr"]].enabled = htmlOn       # Symbology layer
        p[self.l["hFolder"]].enabled = htmlOn   # html output folder
        return

    def updateMessages(self, p): #optional

        return

    def execute(self, p, messages):
        # Force reload and make our logger use ArcGIS feedback
        reloadModules()
        w2py.log.useArcLogging(messages, arcpy)
        
        # Read a single file using our library
        inDataFile = p[self.l["file"]].valueAsText
        outLocation = p[self.l["out"]].valueAsText
        netcdfType = p[self.l["net"]].valueAsText

        makeHtml = p[self.l["html"]].value
        symbols = p[self.l["lyr"]].valueAsText
        hOut = p[self.l["hFolder"]].valueAsText
        
        w2py.log.info("HTML is set to "+str(makeHtml))
        output = w2py.w2.readSingleFileToRaster(inDataFile, outLocation, netcdfType, makeHtml, symbols, hOut)
        # Assign output and we're done
        p[5].value = output
        
        
class MImportW2NetcdfRaster(object):
    """ Tool for importing multiple files from netcdf to raster """
    def __init__(self):
        self.label       = "W2 Netcdf to Raster (multiple)"
        self.description = "Converts multiple National Severe Storms Laboratory data file(s), \
        in WDSSII Netcdf format to raster dataset(s).  Current supports the NSSL LatLonGrid datatype."
        
        # Define a lookup map for our parameters.  This should match the 
        # creation of parameters in getParameterInfo.  We do this to avoid keeping
        # track of the index value changes (which prevents bugs).
        self.l = {"Input":0, "Output":1, "net":2, "html":3, "hFolder":4, "lyr":5}
           
    def getParameterInfo(self):
        
        # The input base directory for data files
        in_dir = folderChoice(False, "input_dir", "Root input directory")
        in_dir.value = w2res.getDataDir()
        out_dir = folderChoice(False, "output_dir", "Root HTML output directory")
        out_dir.value = w2res.getHTMLGenDir()
        
        htmlFolder = folderChoice(False, "html_output", "Output HTML/PNG Folder", False)
        htmlFolder.value = w2py.resource.getHTMLGenDir()
        # Match this order with self.l in __init__
        p = [in_dir, out_dir, netcdfReaderChoice(),  \
             generateHtmlChoice(False), htmlFolder, symbologyChoice()]
        return p

    def isLicensed(self): #optional
        return True

    def updateParameters(self, p): #optional
        # Only require the html folder and settings if the Generate HTML button is on
        htmlOn = p[self.l["html"]].value
        p[self.l["lyr"]].enabled = htmlOn       # Symbology layer
        p[self.l["hFolder"]].enabled = htmlOn   # html output folder
        return

    def updateMessages(self, parameters): #optional
        return

    def execute(self, p, messages):
        # Force reload and make our logger use ArcGIS feedback
        reloadModules()
        w2py.log.useArcLogging(messages, arcpy)
        
        # Read a directory tree using our library
        inFolder = p[self.l["Input"]].valueAsText
        outFolder = p[self.l["Output"]].valueAsText
        netcdfType = p[self.l["net"]].valueAsText
        w2py.w2.readMultipleFiles(inFolder, outFolder, netcdfType)
        #p[2].value = output

        
