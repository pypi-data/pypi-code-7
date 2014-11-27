from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE

from plone.testing import z2

import collective.lastmodified


COLLECTIVE_LASTMODIFIED = PloneWithPackageLayer(
    zcml_package=collective.lastmodified,
    zcml_filename="configure.zcml",
    gs_profile_id="collective.lastmodified:default",
    name="COLLECTIVE_LASTMODIFIED",
)

COLLECTIVE_LASTMODIFIED_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_LASTMODIFIED,),
    name="CollectivelastmodifiedLayer:Integration"
)

COLLECTIVE_LASTMODIFIED_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_LASTMODIFIED, AUTOLOGIN_LIBRARY_FIXTURE, z2.ZSERVER_FIXTURE),
    name="CollectivelastmodifiedLayer:Functional"
)
