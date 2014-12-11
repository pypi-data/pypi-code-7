from setuptools import setup
setup(
    name='reahl',
    version=u'2.0.2',
    description='The Reahl web framework.',
    long_description=u'Reahl is a web application framework for Python programmers.\n\nWith Reahl, programming is done purely in Python, using concepts familiar from GUI programming---like reusable Widgets and Events. There\'s no need for a programmer to know several different languages (HTML, JavaScript, template languages, etc) or to keep up with the tricks of these trades. The abstractions presented by Reahl relieve the programmer from the burden of dealing with the annoying problems of the web: security, accessibility, progressive enhancement (or graceful degradation) and browser quirks.\n\nReahl consists of many different eggs that are not all needed all of the time. This package does not contain much itself, but is an entry point for installing a set of Reahl eggs:\n\nInstall Reahl by installing with pip extras, eg: "pip install reahl[sqlite,dev,doc]" to install everything needed to run Reahl on sqlite, the dev tools and documentation.\n\nSee http://www.reahl.org/docs/current/tutorial/gettingstarted.d.html for installation instructions. ',
    url=u'http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=[],
    py_modules=['setup'],
    include_package_data=False,
    package_data={'': [u'*/LC_MESSAGES/*.mo']},
    namespace_packages=[],
    install_requires=[],
    setup_requires=[],
    tests_require=[],
    test_suite='tests',
    entry_points={
        'reahl.eggs': [
            u'Egg = reahl.component.eggs:ReahlEgg'    ],
                 },
    extras_require={u'doc': [u'reahl-doc>=2.0,<2.1'], u'sqlite': [u'reahl-component>=2.0,<2.1', u'reahl-web>=2.0,<2.1', u'reahl-sqlalchemysupport>=2.0,<2.1', u'reahl-sqlitesupport>=2.0,<2.1', u'reahl-domain>=2.0,<2.1', u'reahl-domainui>=2.0,<2.1', u'reahl-mailutil>=2.0,<2.1', u'reahl-web-elixirimpl>=2.0,<2.1'], u'postgresql': [u'reahl-component>=2.0,<2.1', u'reahl-web>=2.0,<2.1', u'reahl-sqlalchemysupport>=2.0,<2.1', u'reahl-postgresqlsupport>=2.0,<2.1', u'reahl-domain>=2.0,<2.1', u'reahl-domainui>=2.0,<2.1', u'reahl-mailutil>=2.0,<2.1', u'reahl-web-elixirimpl>=2.0,<2.1'], u'dev': [u'reahl-dev>=2.0,<2.1', u'reahl-webdev>=2.0,<2.1', u'reahl-stubble>=2.0,<2.1', u'reahl-tofu>=2.0,<2.1'], u'minimal': [u'reahl-component>=2.0,<2.1', u'reahl-web>=2.0,<2.1', u'reahl-sqlalchemysupport>=2.0,<2.1', u'reahl-sqlitesupport>=2.0,<2.1', u'reahl-postgresqlsupport>=2.0,<2.1', u'reahl-domain>=2.0,<2.1', u'reahl-domainui>=2.0,<2.1', u'reahl-mailutil>=2.0,<2.1', u'reahl-web-elixirimpl>=2.0,<2.1']}
)
