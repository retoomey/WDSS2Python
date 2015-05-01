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
    """ Turn something like 'C:/stuff/test.netcdf.gz' into 'test' """
    return getAbsBaseMulti(os.path.basename(filename))

def getAbsBaseMulti(filename):
    """ We have files like name.netcdf.gz where there are multiple periods.  So this
        function will get rid of all of them in an OS independent manner.  The regular
        splitext only handles one period.  So we call it until it returns the same string
        Turn something like 'C:/stuff/test.netcdf.gz' into 'C:/stuff/test' """
    newfilename = os.path.splitext(filename)[0]
    while newfilename != filename:  # We took at least one '.' off..
        filename = newfilename
        newfilename = os.path.splitext(filename)[0]  # Do it until no more periods come off
    return newfilename

def removeGDBCharacters(filename):
    """ Remove characters that can't be in a GDB name.  I know that at least '-' must be
        removed."""
    filename = filename.replace("-", "_")
    return filename

def getHandledFileTypes():
    """ Get the file types that we can parse """
    return ["netcdf", "nc", "gz"]

def isHandledFileType(filename):
    """ Return True if given filename ends in one of our handled endings """
    handled = False
    for l in getHandledFileTypes():
        if filename.endswith("."+l):
            handled = True
            break
    return handled
        
        