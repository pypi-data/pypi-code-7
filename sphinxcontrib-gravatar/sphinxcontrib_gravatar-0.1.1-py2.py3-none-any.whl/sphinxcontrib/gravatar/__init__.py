# -*- coding: utf-8 -*-
"""
    sphinxcontrib.gravatar
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author: tell-k <ffk2005@gmail.com>
    :copyright: tell-k. All Rights Reserved.
"""
__docformat__ = 'restructuredtext'
__author__ = 'tell-k'
__version__ = '0.1.1'

from sphinxcontrib.gravatar.nodes import (
    gravatar_image,
    html_visit_gravatar_image,
    latex_visit_gravatar_image,
)
from sphinxcontrib.gravatar.directives import GravatarDirective


def setup(app):
    app.add_node(
        gravatar_image,
        html=(html_visit_gravatar_image, None),
        latex=(latex_visit_gravatar_image, None)
    )
    app.add_config_value('gravatar_users', (), 'env')
    app.add_config_value('gravatar_default_size', None, 'env')
    app.add_config_value('gravatar_default_rating', None, 'env')
    app.add_config_value('gravatar_default_image', None, 'env')
    app.add_config_value('gravatar_default_class', "gravatar", 'env')
    app.add_config_value('gravatar_force_default', False, 'env')
    app.add_config_value('gravatar_force_refresh', False, 'env')
    app.add_config_value('gravatar_unlink', False, 'env')
    app.add_config_value('gravatar_default_target', None, 'env')
    app.add_directive('gravatar', GravatarDirective)
