from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

import ngi.notify.datadog


NGI_NOTIFY_DATADOG = PloneWithPackageLayer(
    zcml_package=ngi.notify.datadog,
    zcml_filename='testing.zcml',
    name="NGI_NOTIFY_DATADOG")

NGI_NOTIFY_DATADOG_INTEGRATION = IntegrationTesting(
    bases=(NGI_NOTIFY_DATADOG, ),
    name="NGI_NOTIFY_DATADOG_INTEGRATION")

NGI_NOTIFY_DATADOG_FUNCTIONAL = FunctionalTesting(
    bases=(NGI_NOTIFY_DATADOG, ),
    name="NGI_NOTIFY_DATADOG_FUNCTIONAL")
