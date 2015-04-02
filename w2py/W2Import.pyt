# Robert Toomey
# ArcGIS Python Toolbox for importing custom WDSSII data format into ArcGIS
# We'll try to keep just GUI code here and do all the work in our python command line code

# March/April 2015

import arcpy
import w2

class Toolbox(object):
    def __init__(self):
        self.label =  "WDSSII toolbox"
        self.alias  = "wdssii"

        # List of tool classes associated with this toolbox
        self.tools = [ImportWDSSIINetcdf] 

class ImportWDSSIINetcdf(object):
    def __init__(self):
        self.label       = "Input WDSSII Netcdf File"
        self.description = "Import a WDSSII netcdf file itno ArcGIS."

    def getParameterInfo(self):
        #Define parameter definitions

        # Input Features parameter
        in_features = arcpy.Parameter(
            displayName="Input WDSSII Netcdf2 file",
            name="in_features",
            #datatype="GPFeatureLayer",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")
        
        in_features.filter.list = ["*"]
        
        # Derived Output Features parameter
        out_features = arcpy.Parameter(
            displayName="Output Feature Class",
            name="out_features",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")
        
        #out_features.parameterDependencies = [in_features.name]
        #out_features.schema.clone = True

        parameters = [in_features, out_features]
        return parameters

    def isLicensed(self): #optional
        return True

    def updateParameters(self, parameters): #optional
       # if parameters[0].altered:
       #     parameters[1].value = arcpy.ValidateFieldName(parameters[1].value,
       #                                                   parameters[0].value)
        return

    def updateMessages(self, parameters): #optional
        return

    def execute(self, parameters, messages):
        # We reload our worker script, because refreshing the ArcGIS toolbox doesn't
        # refresh any imported scripts.  And for speed testing in ArcGIS I want it to refresh
        # http://resources.arcgis.com/en/help/main/10.1/index.html#//001500000038000000
        reload(w2)
        w2.readFromArcGIS(parameters, messages)

        inFeatures  = parameters[0].valueAsText
        out_features   = parameters[1].valueAsText
        
        #arcpy.AddField_management(inFeatures, fieldName, 'DOUBLE')

        #arcpy.CalculateField_management(inFeatures,
        #                                fieldName,
        #                                'getSinuosity(!shape!)',
        #                                'PYTHON_9.3',
        #                                expression)
