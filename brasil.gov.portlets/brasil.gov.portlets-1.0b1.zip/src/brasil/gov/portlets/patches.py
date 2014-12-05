# -*- coding: utf-8 -*-
from brasil.gov.portlets.config import PROJECTNAME
from plone.app.portlets.portlets.base import Renderer

import logging

logger = logging.getLogger(PROJECTNAME)


def portlet_renderer():
    def _has_image_field(self, obj):
        """Return True if the object has an image field.

        :param obj: [required]
        :type obj: content object
        """
        if hasattr(obj, 'image'):  # Dexterity
            return True
        elif hasattr(obj, 'Schema'):  # Archetypes
            return 'image' in obj.Schema().keys()
        else:
            return False

    setattr(Renderer,
            '_has_image_field',
            _has_image_field)
    logger.info('Patched portlet Renderer class')


def run():
    portlet_renderer()
