

######################################################################################
#
# YOU CAN / SHOULD EDIT THE FOLLOWING SETTING
#
######################################################################################

PKG_NAME = 'hires'

VERSION = (0, 0, 11)

### install package as emzed extension ? #############################################
#   -> package will appear in emzed.ext namespace after installation

IS_EXTENSION = True


### install package as emzed app ?  ##################################################
#   -> can be started as app.hires()
#   set this variable to None if this is a pure extension and not an emzed app

APP_MAIN = None


### author information ###############################################################

AUTHOR = 'Uwe Schmitt'
AUTHOR_EMAIL = 'uschmitt@uweschmitt.info'
AUTHOR_URL = None


### package descriptions #############################################################

DESCRIPTION = "algorithms for high resolution lcms"
LONG_DESCRIPTION = """

High resolution LCMS allows identification algorithms solely based
on mass and retention times. This emzed package contains algorithms for
grouping and annotating mass traces in respect of isotope shifts and
adduct assignments.
"""


LICENSE = "http://opensource.org/licenses/GPL-3.0"


######################################################################################
#                                                                                    #
# DO NOT TOUCH THE CODE BELOW UNLESS YOU KNOW WHAT YOU DO !!!!                       #
#                                                                                    #
#                                                                                    #
#       _.--""--._                                                                   #
#      /  _    _  \                                                                  #
#   _  ( (_\  /_) )  _                                                               #
#  { \._\   /\   /_./ }                                                              #
#  /_"=-.}______{.-="_\                                                              #
#   _  _.=('""')=._  _                                                               #
#  (_'"_.-"`~~`"-._"'_)                                                              #
#   {_"            "_}                                                               #
#                                                                                    #
######################################################################################


if APP_MAIN is not None:
    try:
        mod_name, fun_name = APP_MAIN.split(":")
        exec "import %s as _mod" % mod_name
        fun = getattr(_mod, fun_name)
    except:
        raise Exception("invalid specification %r of APP_MAIN" % APP_MAIN)

VERSION_STRING = "%s.%s.%s" % VERSION

ENTRY_POINTS = dict()
ENTRY_POINTS['emzed_package'] = [ "package = " + PKG_NAME, ]
if IS_EXTENSION:
    ENTRY_POINTS['emzed_package'].append("extension = " + PKG_NAME)
if APP_MAIN is not None:
    ENTRY_POINTS['emzed_package'].append("main = %s" % APP_MAIN)


if __name__ == "__main__":   # allows import setup.py for version checking

    import distutils.config

    from setuptools import setup
    setup(name=PKG_NAME,
        packages=[ PKG_NAME ],
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=AUTHOR_URL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        license=LICENSE,
        version=VERSION_STRING,
        entry_points = ENTRY_POINTS
        )
