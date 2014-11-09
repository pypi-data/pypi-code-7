import xml.etree.ElementTree as XML


def travis(parser, xml_parent, data):
    """yaml: travis
    """
    ruby_object = XML.SubElement(
        XML.SubElement(xml_parent, 'ruby-proxy-object'),
        'ruby-object')
    ruby_object.set('ruby-class', 'Jenkins::Tasks::BuilderProxy')
    ruby_object.set('pluginid', 'travis-yml')

    pluginid = XML.SubElement(ruby_object, 'pluginid')
    pluginid.set('pluginid', 'travis-yml')
    pluginid.set('ruby-class', 'String')
    pluginid.text = 'travis-yml'

    obj = XML.SubElement(ruby_object, 'object')
    obj.set('ruby-class', 'TravisYmlBuilder')
    obj.set('pluginid', 'travis-yml')
