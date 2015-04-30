'''
Log utilities

We create a simple log that can wrap around console or ArcGIS messages,
as well as the ArcGIS progressor dialog abilities.

This is so we can easily call our tools  from an ArcGIS toolbox, OR from a
console command, possibly even without arcpy installed even.  For example,
a custom algorithm might be designed to run with or without arcpy access

Designed to be binary: text Or arcgis.  Adding a third type of logging 
would require a refactor or making log into a class

@author: Robert Toomey (retoomey)
'''

import sys

# Do we have arcpy access?
haveArcpy = False
arcMessage = None
arcProgress = None
debug = True

def useArcLogging(message, progressor):
    """ Set up ArcGIS messaging.  All prints will go to this
    """
    global haveArcpy
    global arcMessage
    global arcProgress
    haveArcpy = True
    arcMessage = message
    arcProgress = progressor

def setDefaultProgress(text2):
    """ Wrap the SetProgressor ability to arcpy or console """
    if haveArcpy:
        arcProgress.SetProgressor("default", text2)
    else:
        info("Done...")
        
def setStepProgress(text, minv, maxv, interval):
    """ Wrap the SetProgressor ability to arcpy or console """
    if haveArcpy:
        arcProgress.SetProgressor("step", text, minv, maxv, interval)
    else:
        info("Done...")        
        
def setProgressLabel(text):
    """ Wrap the SetProgressorLabel ability to arcpy or console """
    if haveArcpy:
        arcProgress.SetProgressorLabel(text)
    else:
        info(text)
  
def setProgressPosition():
    """ Wrap the SetProgressorPosition ability to arcpy or console """
    if haveArcpy:
        arcProgress.SetProgressorPosition()
    else:
        info(".")
        
def resetProgress():
    """ Wrap the ResetProgressor ability to arcpy or console """
    if haveArcpy:
        arcProgress.ResetProgressor()
    else:
        info("Done...")
        
def info(text, newline=True):
    """ Log info.  We wrap logging functions to allow us running from 
        command line or with ArcGIS toolbox
    """
    if haveArcpy:
        arcMessage.addMessage(text)
    else:
        sys.stdout.write(text)
        if newline:
            sys.stdout.write("\n")

def debug(text):
    """ Log debug statements.  We wrap logging functions to allow us running from 
        command line or with ArcGIS toolbox
    """
    if debug:
        info(text)
        
def error(text, newline=True):
    """ Log errors.  We wrap logging functions to allow us running from 
        command line or with ArcGIS toolbox
    """
    if haveArcpy:
        arcMessage.addError(text)
    else:
        sys.stderr.write(text)
        if newline:
            sys.stderr.write("\n")

