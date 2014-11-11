# coding=utf-8
__author__ = 'kohlmannj'


class Config(object):
    DEBUG = False
    TESTING = False
    DEFAULT_CORPUS_NAME = "ShakespeareChunkedOptimized_50"
    NAME = u"Serendip[ity]"
    WEB_ROOT = "/"
    TOPICMODEL_STATIC_CACHE = True
    TOPICMODEL_STATIC_SVG_CACHE = False
    TEXTVIEWER_DEFAULT_NUM_TAG_MAPS = 8000


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    NAME = u"Ser·ənˈ·dip[·itē] (Dev)"


class TestingConfig(DevelopmentConfig):
    TESTING = True
    NAME = "u\"Ser\\xb7\\u0259n\\u02c8\\xb7dip[\\xb7it\\u0113]\" (Testing)"
