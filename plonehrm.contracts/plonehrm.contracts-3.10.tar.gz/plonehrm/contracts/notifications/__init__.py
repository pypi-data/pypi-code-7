try:
    import zope.annotation
except ImportError:
    # BBB for Zope 2.9
    import zope.app.annotation
    import zope.app.annotation.interfaces
    import sys
    sys.modules['zope.annotation'] = zope.app.annotation
    sys.modules['zope.annotation.interfaces'] = zope.app.annotation.interfaces
