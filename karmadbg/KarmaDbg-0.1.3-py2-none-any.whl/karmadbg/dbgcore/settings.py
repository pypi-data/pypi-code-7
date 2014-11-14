import xml.etree.ElementTree as xmltree

class DbgSettings(object):

    def __init__(self, filename):
        self.filename=filename
        self.rootxml = xmltree.parse(filename).getroot()

    @property
    def workspaces(self):
        return [ DbgWorkspace(workspace) for workspace in self.rootxml.findall("./Workspace") ]

    @property
    def styles(self):

        return { getStrAttribute(style, "name", "default" ) : getStrAttribute(style, "body") for style in self.rootxml.findall("./Style") }


class DbgWorkspace(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def mainWindow(self):
        xmlelem=self.xmlelem.find("./MainWindow")
        return DbgMainWindowSettings(xmlelem)

    @property
    def dbgEngExtensions(self):
        xmlelem=self.xmlelem.find("./DbgEngExtensions")
        return [ DbgEngExtensionSetting(ext) for ext in xmlelem.findall("./Extension") ]

    @property
    def widgets(self):
        xmlelem=self.xmlelem.find("./Widgets")
        return [ WidgetSettings(widget) for widget in xmlelem.findall("./Widget") ]

    @property
    def actions(self):
        xmlelem=self.xmlelem.find("./Actions")
        return [ ActionSettings(action) for action in xmlelem.findall("./Action") ]

    @property
    def dialogs(self):
        xmlelem=self.xmlelem.find("./Dialogs")
        return [ DialogSettings(action) for action in xmlelem.findall("./Dialog") ]

    @property
    def style(self):
        return DbgStyleSettings(self.xmlelem.find("./Style"))

    @property
    def textCodec(self):
        xmlelem = self.xmlelem.find("./TextCodec")
        return DbgTextCodecSettings(xmlelem) if xmlelem != None else None

    @property
    def mainMenu(self):
        return MainMenuSettings(self.xmlelem.find("./MainMenu"))


class DbgMainWindowSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def width(self):
        return getIntAttribute( self.xmlelem, "width", 800 )

    @property
    def height(self):
        return getIntAttribute( self.xmlelem , "height", 600 )

    @property
    def title(self):
        return getStrAttribute( self.xmlelem , "title", "Window Title" )


class MainMenuSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def module(self):
        return getStrAttribute(self.xmlelem, "module")
    
    @property
    def className(self):
        return getStrAttribute(self.xmlelem, "className")

    @property
    def menuItems(self):
        return [ MenuItemSettings(item) for item in self.xmlelem.findall("./MenuItem") ]


class MenuItemSettings(object):

    def __init__(self,xmlelem):
        self.xmlelem=xmlelem

    @property
    def name(self):
        return getStrAttribute( self.xmlelem , "name")

    @property
    def actionName(self):
        return getStrAttribute( self.xmlelem , "actionName")

    @property
    def displayName(self):
        return getStrAttribute( self.xmlelem , "displayName")
        
    @property
    def separator(self):
        return getBoolAttribute(self.xmlelem, "separator")

    @property
    def toggleWidget(self):
        return getStrAttribute(self.xmlelem, "toggleWidget")

    @property
    def menuItems(self):
        return [ MenuItemSettings(item) for item in self.xmlelem.findall("./MenuItem") ]

class DbgStyleSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def fileName(self):
        return getStrAttribute(self.xmlelem, "fileName") if self.xmlelem != None else ""

    @property
    def text(self):
        return getStrAttribute(self.xmlelem, "text") if self.xmlelem != None else ""

class DbgTextCodecSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def name(self):
         return getStrAttribute(self.xmlelem, "name") if self.xmlelem != None else ""

    

class DbgEngExtensionSetting(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def name(self):
         return getStrAttribute(self.xmlelem, "name", self.path )

    @property
    def path(self):
        return getStrAttribute(self.xmlelem, "path")

    @property
    def startup(self):
        return getBoolAttribute(self.xmlelem, "startup")


class WidgetSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def name(self):
         return getStrAttribute(self.xmlelem, "name")

    @property
    def module(self):
        return getStrAttribute(self.xmlelem, "module")
    
    @property
    def className(self):
        return getStrAttribute(self.xmlelem, "className")

    @property
    def behaviour(self):
        return getStrAttribute(self.xmlelem, "behaviour")

    @property
    def visible(self):
        return getBoolAttribute(self.xmlelem, "visible")

    @property
    def title(self):
        return getStrAttribute(self.xmlelem, "title")

class DialogSettings(object):

    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def name(self):
         return getStrAttribute(self.xmlelem, "name")

    @property
    def module(self):
        return getStrAttribute(self.xmlelem, "module")
    
    @property
    def className(self):
        return getStrAttribute(self.xmlelem, "className")


class ActionSettings(object):
    def __init__(self, xmlelem):
        self.xmlelem = xmlelem

    @property
    def name(self):
        return getStrAttribute(self.xmlelem, "name")

    @property
    def displayName(self):
        return getStrAttribute(self.xmlelem, "displayName", self.name )

    @property
    def shortcut(self):
        return getStrAttribute(self.xmlelem, "shortcut")

    @property
    def module(self):
        return getStrAttribute(self.xmlelem, "module")
    
    @property
    def funcName(self):
        return getStrAttribute(self.xmlelem, "funcName")

    @property
    def toggleWidget(self):
        return getStrAttribute(self.xmlelem, "toggleWidget")

    @property
    def showDialog(self):
        return getStrAttribute(self.xmlelem, "showDialog")

def getIntAttribute(xmlelem,name,default=0):
    try:
        val = xmlelem.get( name, default )
        return int(val)
    except ValueError:
        pass

    try:
        return int(val,16)
    except ValueError:
        pass

    return default

def getStrAttribute(xmlelem,name,default=""):
    return str( xmlelem.get( name, default ) )

def getBoolAttribute(xmlelem, name, default=False):
    val=xmlelem.get(name)
    if val==None:
        return default
    return val.lower()=="true"
