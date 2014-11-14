from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

import collective.viewlet.pythonscript


COLLECTIVE_VIEWLET_PYTHONSCRIPT = PloneWithPackageLayer(
    zcml_package=collective.viewlet.pythonscript,
    zcml_filename='testing.zcml',
    gs_profile_id='collective.viewlet.pythonscript:testing',
    name="COLLECTIVE_VIEWLET_PYTHONSCRIPT")

COLLECTIVE_VIEWLET_PYTHONSCRIPT_INTEGRATION = IntegrationTesting(
    bases=(COLLECTIVE_VIEWLET_PYTHONSCRIPT, ),
    name="COLLECTIVE_VIEWLET_PYTHONSCRIPT_INTEGRATION")

COLLECTIVE_VIEWLET_PYTHONSCRIPT_FUNCTIONAL = FunctionalTesting(
    bases=(COLLECTIVE_VIEWLET_PYTHONSCRIPT, ),
    name="COLLECTIVE_VIEWLET_PYTHONSCRIPT_FUNCTIONAL")
