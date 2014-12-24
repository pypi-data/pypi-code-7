#!/usr/bin/env python
# -*- coding: utf-8 -*-

class By(object):
    """
    Set of supported locator strategies.
    """

    ID = "id"
    XPATH = "xpath"
    LINK_TEXT = "link text"
    PARTIAL_LINK_TEXT = "partial link text"
    NAME = "name"
    TAG_NAME = "tag name"
    CLASS_NAME = "class name"
    CSS_SELECTOR = "css selector"

    @classmethod
    def is_valid(cls, by):
        for attr in dir(cls):
            if by == getattr(cls, attr):
                return True
        return False
