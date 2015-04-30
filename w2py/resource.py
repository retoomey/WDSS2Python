'''
Resource handling

Keep track of the names/locations of any static resources we use, file types.

@author: Robert Toomey (retoomey)
'''

import os

def getScriptDir():
    """ Get root location this script is running from. Found this example on google.
        Basically use the file path of THIS module, but go up one directory """
    upOne = (os.path.join( os.path.dirname ( __file__), os.pardir))
    return os.path.abspath(upOne)

def getResourceDir():
    """ Get the location of our 'resource' directory. We use this to
        find our resources.  Found this example on google """
    return os.path.join(getScriptDir(), "resource")

def getArcgisDir():
    """ Get the location of our arcgis data file directory """
    return os.path.join(getResourceDir(), "arcgis")

def getDataDir():
    """ Get the location of our arcgis data file directory """
    return os.path.join(getResourceDir(), "exampleNsslData")

def getHTMLGenDir():
    """ Get the location of a default HTML generation directory """
    return os.path.join(getResourceDir(), "HTML")

def getArcgisFilename(filename):
    """ Get the location of a file in our arcgis data file directory """
    return os.path.join(getArcgisDir(), filename)

def getDataFilename(filename):
    """ Get the location of a file in our arcgis data file directory """
    return os.path.join(getDataDir(), filename)

def getSymbologyLayer():
    """ Get the location of our default symbology lyr file for raster generation
        and html output """
    return getArcgisFilename("cloudcover.lyr")

def getUSAMapLayer():
    """ Get the location of our USA map we provide for CONUS html generation"""
    return getArcgisFilename("usa.lyr")

def getTempFile(rootfolder, filename):
    """ Get a full temp file location given a rootfolder and name """
    return os.path.join(rootfolder, filename)   
                    
def getBaseMulti(filename):
    """ We have files like name.netcdf.gz where there are multiple periods.  So this
        function will get rid of all of them in an OS independent manner.  The regular
        splitext only handles one period. """
    filename = os.path.basename(filename)
    count = 0
    while count < 4 or "." in filename:
        count += 1
        filename = os.path.splitext(filename)[0]
    return filename

def getHandledFileTypes():
    """ Get the file types that we can parse """
    return ["netcdf", "nc", "gz"]