from setuptools import setup
setup(
    name='reahl',
    version=u'2.1.2',
    description=u'The Reahl web framework.',
    long_description=u'Reahl is a web application framework for Python programmers.\n\nWith Reahl, programming is done purely in Python, using concepts familiar from GUI programming---like reusable Widgets and Events. There\'s no need for a programmer to know several different languages (HTML, JavaScript, template languages, etc) or to keep up with the tricks of these trades. The abstractions presented by Reahl relieve the programmer from the burden of dealing with the annoying problems of the web: security, accessibility, progressive enhancement (or graceful degradation) and browser quirks.\n\nReahl consists of many different eggs that are not all needed all of the time. This package does not contain much itself, but is an entry point for installing a set of Reahl eggs:\n\nInstall Reahl by installing with extras, eg: easy_install "reahl[elixir,sqlite,dev,doc]" to install everything needed to run Reahl on sqlite, the dev tools and documentation.\n\nSee http://www.reahl.org/docs/current/tutorial/gettingstarted.d.html for installation instructions. ',
    url=u'http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=[],
    py_modules=[u'setup'],
    include_package_data=False,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=[],
    install_requires=[],
    setup_requires=[],
    tests_require=[],
    test_suite=u'tests',
    entry_points={
        u'reahl.eggs': [
            u'Egg = reahl.component.eggs:ReahlEgg'    ],
                 },
    extras_require={u'web': [u'reahl-component>=2.1,<2.2', u'reahl-web>=2.1,<2.2', u'reahl-mailutil>=2.1,<2.2'], u'all': [u'reahl-component>=2.1,<2.2', u'reahl-web>=2.1,<2.2', u'reahl-mailutil>=2.1,<2.2', u'reahl-sqlalchemysupport>=2.1,<2.2', u'reahl-web-declarative', u'reahl-domain>=2.1,<2.2', u'reahl-domainui>=2.1,<2.2', u'reahl-postgresqlsupport>=2.1,<2.2', u'reahl-sqlitesupport>=2.1,<2.2', u'reahl-dev>=2.1,<2.2', u'reahl-webdev>=2.1,<2.2', u'reahl-stubble>=2.1,<2.2', u'reahl-tofu>=2.1,<2.2', u'reahl-doc>=2.1,<2.2'], u'postgresql': [u'reahl-postgresqlsupport>=2.1,<2.2'], u'doc': [u'reahl-doc>=2.1,<2.2'], u'sqlite': [u'reahl-sqlitesupport>=2.1,<2.2'], u'dev': [u'reahl-dev>=2.1,<2.2', u'reahl-webdev>=2.1,<2.2', u'reahl-stubble>=2.1,<2.2', u'reahl-tofu>=2.1,<2.2'], u'elixir': [u'reahl-sqlalchemysupport>=2.1,<2.2', u'reahl-domain>=2.1,<2.2', u'reahl-domainui>=2.1,<2.2', u'reahl-web-elixirimpl>=2.1,<2.2']}
)
