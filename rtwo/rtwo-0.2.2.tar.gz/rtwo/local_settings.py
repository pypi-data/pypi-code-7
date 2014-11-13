import logging
import os

import threepio

import rtwo

# Openstack provider secrets
OPENSTACK_ADMIN_KEY="atmoadmin"
OPENSTACK_ADMIN_SECRET="NoMoreSecrets9292676HanShotFirst"
OPENSTACK_AUTH_URL='http://heimdall.iplantcollaborative.org:5000/v2.0'
OPENSTACK_ADMIN_URL=OPENSTACK_AUTH_URL.replace("5000","35357")
OPENSTACK_ADMIN_TENANT="atmoadminTenant"
OPENSTACK_DEFAULT_REGION="ValhallaRegion"
OPENSTACK_DEFAULT_ROUTER="public_router"

# Openstack provider dictionaries
OPENSTACK_ARGS = {
    'username': OPENSTACK_ADMIN_KEY,
    'password': OPENSTACK_ADMIN_SECRET,
    'tenant_name': OPENSTACK_ADMIN_TENANT,
    'auth_url': OPENSTACK_ADMIN_URL,
    'region_name': OPENSTACK_DEFAULT_REGION
}
OPENSTACK_NETWORK_ARGS = {
    'auth_url': OPENSTACK_ADMIN_URL,
    'region_name': OPENSTACK_DEFAULT_REGION,
    'router_name': OPENSTACK_DEFAULT_ROUTER
}

LOGGING_LEVEL = logging.INFO
DEP_LOGGING_LEVEL = logging.WARN # Logging level for dependencies.
LOG_FILENAME = os.path.abspath(os.path.join(
    os.path.dirname(rtwo.__file__),
    '..',
    'logs/rtwo.log'))
threepio.initialize("rtwo",
                    log_filename=LOG_FILENAME,
                    app_logging_level=LOGGING_LEVEL,
                    dep_logging_level=DEP_LOGGING_LEVEL)

EUCA_ADMIN_KEY=""
EUCA_ADMIN_SECRET=""
SERVER_URL=""
INSTANCE_SERVICE_URL=""
ATMOSPHERE_VNC_LICENSE=""
