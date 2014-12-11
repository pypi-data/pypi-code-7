#  (C) Catchoom Technologies S.L.
#  Licensed under the MIT license.
#  https://github.com/catchoom/craftar-python/blob/master/LICENSE
#  All warranties and liabilities are disclaimed.

"Default settings"

import platform

RECOGNITION_HOSTNAME = 'https://search.craftar.net'
MANAGEMENT_HOSTNAME = 'https://my.craftar.net'

RECOGNITION_API_VERSION = "v1"
MANAGEMENT_API_VERSION = "v0"

USER_AGENT = "CraftAR/1.3.2 (python %s)" % platform.python_version()

DEFAULT_QUERY_MIN_SIZE = 270  # default image transformation parameters
DEFAULT_IMG_QUALITY = 80  # for jpeg compression, recommended range [75-85]

ALLOWED_IMG_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
ALLOWED_OBJECT_TYPES = ["collection", "item", "image", "token", "media"]
