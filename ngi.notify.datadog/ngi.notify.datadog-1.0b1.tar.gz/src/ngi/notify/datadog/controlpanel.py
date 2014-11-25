# encoding: utf-8
"""
Created on 07/18/14

@author: Takashi NAGAI
"""
from zope import schema
from zope.interface import Interface
from plone.app.registry.browser import controlpanel
from ngi.notify.datadog import _


class IDatadog(Interface):
    """ Datadog settings """

    use_dogstatsd = schema.Bool(
        title=_(u'use_dogstatsd_tetxt',
                default=u"Using the DogStatsD"),
        description=_(u"use_dogstatsd_help", default=u'Please check when using the DogStatsD.'),
        default=True,
        required=True)


    statsd_host = schema.TextLine(
        title=_(u'statsd_port_title', default=u'DogStatsD Host'),
        description=_(u"statsd_port_help",
                      default=u'Please enter DogStatsD host when you are using the DogStatsD.'),
        required=False,
        default=u'localhost'
    )

    statsd_port = schema.TextLine(
        title=_(u'statsd_port_title', default=u'DogStatsD Port'),
        description=_(u"statsd_port_help",
                      default=u'Please enter DogStatsD port when you are using the DogStatsD.'),
        required=False,
        default=u'8125'
    )

    api_key = schema.TextLine(
        title=_(u'api_key_title', default=u'DataDog API key'),
        description=_(u"api_key_help",
                      default=u'Please enter API key when you are not using the DogStatsD.'),
        required=False,
    )

    application_key = schema.TextLine(
        title=_(u'application_key_title', default=u'DataDog Application key'),
        description=_(u"application_key_help",
                      default=u'Please enter Application key when you are not using the DogStatsD.'),
        required=False,
    )

    host_name = schema.TextLine(
        title=_(u'host_name_title', default=u'Host Name'),
        description=_(u"host_name_help",
                      default=u'Please enter Host name when you are not using the DogStatsD.'),
        required=False,
    )


class DatadogEditForm(controlpanel.RegistryEditForm):
    """
    Datadog edit form
    """

    schema = IDatadog
    label = _(u'datadog_cp_label', default=u'Notify events to DataDog')
    description = _(u'datadog_cp_help', default=u'Settings')

    def updateWidgets(self):
        super(DatadogEditForm, self).updateWidgets()


class DatadogControlPanel(controlpanel.ControlPanelFormWrapper):
    """
    Datadog Control Panel
    """
    form = DatadogEditForm
