# -*- coding:utf-8 -*-

from setuptools import find_packages
from setuptools import setup

version = '1.0rc3'
description = u'Pacote de politicas do Portal Modelo.'
long_description = (
    open('README.rst').read() + '\n' +
    open('CONTRIBUTORS.rst').read() + '\n' +
    open('CHANGES.rst').read()
)

setup(
    name='interlegis.portalmodelo.policy',
    version=version,
    description=description,
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='interlegis portalmodelo egov plone brasil',
    author='Programa Interlegis',
    author_email='ti@interlegis.leg.br',
    url='https://github.com/interlegis/interlegis.portalmodelo.policy',
    license='GPLv2',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['interlegis', 'interlegis.portalmodelo'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'brasil.gov.vcge',
        'collective.contentrules.mailtogroup',
        'collective.cover',
        'collective.flowplayer',
        'collective.polls',
        'collective.upload',
        'collective.weather',
        'cssselect',
        'five.grok',
        'interlegis.intranetmodelo.policy',
        'interlegis.portalmodelo.api',
        'interlegis.portalmodelo.buscadores',
        'interlegis.portalmodelo.ombudsman',
        'interlegis.portalmodelo.pl',
        'interlegis.portalmodelo.theme',
        'interlegis.portalmodelo.transparency',
        'lxml >=3.2.2',
        'plone.api',
        'plone.app.discussion',
        'plone.app.event [archetypes] <1.2',
        'plone.app.upgrade',
        'plone.formwidget.captcha',
        'plone.i18n',
        'plone.portlets',
        'plone.registry',
        'Products.AROfficeTransforms',
        'Products.CMFPlone >=4.3',
        'Products.CMFQuickInstallerTool',
        'Products.EasyNewsletter',
        'Products.GenericSetup',
        'Products.OpenXml',
        'Products.Ploneboard',
        'Products.PloneFormGen',
        'Products.windowZ',
        'sc.blog',
        'sc.embedder',
        'sc.galleria.support',
        'sc.social.like',
        'setuptools',
        'Solgema.fullcalendar',
        'z3c.unconfigure',
        'zope.component',
        'zope.i18nmessageid',
        'zope.interface',
    ],
    extras_require={
        'test': [
            'plone.app.robotframework',
            'plone.app.testing [robot] >=4.2.2',
            'plone.testing',
            'Products.CMFPlacefulWorkflow',
        ],
    },
    entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
