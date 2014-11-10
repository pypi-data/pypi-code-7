import os

__version__ = '0.1.%s' + (os.environ.get("CIRCLE_BUILD_NUM") or "snowflake")

from consul_ha import ConsulHa
