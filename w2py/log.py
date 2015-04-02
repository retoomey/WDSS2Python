'''
Log utilities

We create a simple log that can wrap around console or ArcGIS messages.
This is so we can easily call this from an ArcGIS toolbox, or from a
console command. Might be better as a class if we get anymore complicated
Very likely arcpy has this functionaliy built in somewhere...

@author: Robert Toomey
'''

# Do we have arc messaging?
haveArcMessage = False
arcMessage = None
debug = False

def useArcLogging(message):
    """ Set up ArcGIS messaging.  All prints will go to this
    """
    global haveArcMessage
    global arcMessage
    haveArcMessage = True
    arcMessage = message

def info(text):
    """ Log info.  We wrap logging functions to allow us running from 
        command line or with ArcGIS toolbox
    """
    global haveArcMessage
    global arcMessage
    if haveArcMessage:
        arcMessage.addMessage(text)
    else:
        print text

def debug(text):
    """ Log debug statements.  We wrap logging functions to allow us running from 
        command line or with ArcGIS toolbox
    """
    global debug
    if debug:
        info(text)
        
def error(text):
    """ Log errors.  We wrap logging functions to allow us running from 
        command line or with ArcGIS toolbox
    """
    global haveArcMessage
    global arcMessage
    if haveArcMessage:
        arcMessage.addError(text)
    else:
        print text

