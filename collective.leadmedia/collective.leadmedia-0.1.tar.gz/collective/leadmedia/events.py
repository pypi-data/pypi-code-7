# Handling Events
from zope.annotation.interfaces import IAnnotations
from Products.CMFCore.utils import getToolByName

def reindexMedia(object, event):
    """
        Reindexes leadmedia catalog indexes
    """

    if object.id != 'slideshow':
        object.reindexObject()
        object.reindexObject(idxs=["hasMedia"])
        object.reindexObject(idxs=["leadMedia"])

        if hasattr(object.getParentNode(), "meta_type"):
            if object.getParentNode().meta_type == "Dexterity Container" and object.getParentNode().portal_type != "Folder":
                reindexMedia(object.getParentNode(), event)
    
    elif object.id == 'slideshow':
        if hasattr(object.getParentNode(), "meta_type"):
            if object.getParentNode().meta_type == "Dexterity Container" and object.getParentNode().portal_type != "Folder":
                reindexMedia(object.getParentNode(), event)

def objectAddedEvent(object, event):
    pt = getToolByName(object, "portal_types")

    objectType = pt.getTypeInfo(object)
    allowType = objectType.allowType("Folder")

    if object.portal_type != "Folder" and allowType:
        if 'slideshow' not in object.objectIds():
            print "Add slideshow folder."

            object.invokeFactory(
                type_name="Folder",
                id=u'slideshow',
                title='slideshow',
            )

            folder = object['slideshow']

            try:
              folder.portal_workflow.doActionFor(folder, "publish", comment="Slideshow content automatically published")
              object.reindexObject()
            except:
              pass
    