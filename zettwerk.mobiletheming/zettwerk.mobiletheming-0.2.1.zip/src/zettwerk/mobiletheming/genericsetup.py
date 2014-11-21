from lxml import etree

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from zettwerk.mobiletheming.interfaces import IMobileThemingSettings


def importSettings(context):
    """ import the settings """
    data = context.readDataFile('mobiletheming.xml')
    if not data:
        return

    settings = getUtility(IRegistry) \
        .forInterface(IMobileThemingSettings, False)

    tree = etree.fromstring(data)

    themename = tree.find('themename')
    if themename is not None:
        value = themename.text.strip()
        ## todo: skip unavailable themes
        settings.themename = value

    hostnames = tree.find('hostnames')
    if hostnames is not None:
        values = []
        for element in hostnames.findall('element'):
            values.append(element.text.strip())
        settings.hostnames = tuple(values)

    ipad = tree.find('ipad')
    if ipad is not None:
        value = ipad.text.strip()
        if value.lower() in ("y", "yes", "true", "t", "1", "on",):
            settings.ipad = True
        elif value.lower() in ("n", "no", "false", "f", "0", "off",):
            settings.ipad = False
        else:
            raise ValueError("%s is not a valid value for <ipad />" % value)

    tablets = tree.find('tablets')
    if tablets is not None:
        value = tablets.text.strip()
        if value.lower() in ("y", "yes", "true", "t", "1", "on",):
            settings.tablets = True
        elif value.lower() in ("n", "no", "false", "f", "0", "off",):
            settings.tablets = False
        else:
            raise ValueError("%s is not a valid value for <tablets />" % value)


def exportSettings(context):
    """ export the settings """
    settings = getUtility(IRegistry) \
        .forInterface(IMobileThemingSettings, False)

    filename = 'mobiletheming.xml'

    root = etree.Element('settings')
    themename = etree.SubElement(root, 'themename')
    themename.text = settings.themename

    hostnames = etree.SubElement(root, 'hostnames')
    for hostname in settings.hostnames:
        entry = etree.SubElement(hostnames, 'element')
        entry.text = hostname

    ipad = etree.SubElement(root, 'ipad')
    ipad.text = unicode(settings.ipad)

    tablets = etree.SubElement(root, 'tablets')
    tablets.text = unicode(settings.tablets)

    body = '<?xml version="1.0"?>\n' + etree.tostring(root, pretty_print=True)
    context.writeDataFile(filename, body, 'text/xml')
