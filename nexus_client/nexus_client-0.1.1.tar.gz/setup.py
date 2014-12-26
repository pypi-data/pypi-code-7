from distutils.core import setup
setup(
    name='nexus_client',
    packages=['nexus_client'],  # this must be the same as the name above
    version='0.1.1',
    description='Python client for Nexus.',
    author='Paul Krohn',
    author_email='paul@daemonize.com',
    url='https://github.com/paul-krohn/python-nexus',
    download_url='https://github.com/paul-krohn/python-nexus/tarball/0.1.1',
    keywords=['nexus'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Software Distribution',
        'Topic :: System :: Systems Administration',

    ],
    install_requires=['requests>=1.0', 'lxml']
)
