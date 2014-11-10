from django import template
register = template.Library()
import os.path
from django.template.defaultfilters import stringfilter

@register.assignment_tag
def getJsStatics(widgetTypeSet):
    static_list = []
    STATIC_DIR =  os.path.abspath(os.path.join(os.path.dirname(__file__),"../static/geoprisma/widgets"))
    for dirpath,dirnames,filenames in os.walk(STATIC_DIR):
        for widgetType in widgetTypeSet:
            if widgetType in dirpath:
                if not "geoextux_redliningpanel" in dirpath and \
                   not "filetreepanel" in dirpath and \
                   not "initialview" in dirpath and \
                   not "measuretool" in dirpath and \
                   not "featurepanel_selector" in dirpath and \
                   not "editfeature_confirm" in dirpath:
                    for filename in filenames:
                        splitDirpath = dirpath.split("/")
                        joinIndex = ""
                        try:
                            joinIndex =  splitDirpath.index("widgets")
                        except ValueError:
                            joinIndex = ""
                        if joinIndex != "":
                            dirpath = "/".join(splitDirpath[joinIndex:len(splitDirpath)])
                            splitFileName = filename.split(".")
                            if splitFileName[-1] == "js" :
                                static_list.append("geoprisma/"+ dirpath + "/" +  filename)
    return static_list

@register.assignment_tag
def getCssStatics(widgetTypeSet):
    static_list = []
    STATIC_DIR =  os.path.abspath(os.path.join(os.path.dirname(__file__),"../static/geoprisma/widgets"))
    for dirpath,dirnames,filenames in os.walk(STATIC_DIR):
        for widgetType in widgetTypeSet:
            if widgetType in dirpath:
                if not "featurepanel_selector" in dirpath:
                    for filename in filenames:
                        splitDirpath = dirpath.split("/")
                        joinIndex = ""
                        try:
                            joinIndex =  splitDirpath.index("widgets")
                        except ValueError:
                            joinIndex = ""
                        if joinIndex != "":
                            dirpath = "/".join(splitDirpath[joinIndex:len(splitDirpath)])
                            splitFileName = filename.split(".")
                            if splitFileName[-1] == "css" :
                                static_list.append("geoprisma/"+ dirpath + "/" +  filename)
    return static_list

@register.filter
@stringfilter
def template_exists(value):
    try:
        template.loader.get_template(value)
        return True
    except template.TemplateDoesNotExist:
        return False
