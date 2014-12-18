from setuptools import setup

setup(name='dsapi',
        version='0.6-beta',
        description='Ingenuity Upload and Status Python Helper scripts and DatastreamAPI library',
        long_description='QIAGEN/Ingenuity Datastream API For pythonic upload, download and status checking of packages submitted to Ingenuity\'s various annotation services',
        url='https://github.com/QIAGENDatastream/dsapi', 
        download_url='https://github.com/QIAGENDatastream/dsapi/archive/v0.6-beta.tar.gz',
        author="Chris Harris",
        author_email="Chris.Harris@Qiagen.com",
        license="GPLv3",
        packages=['dsapi'],
        install_requires=['requests',
            'logging',
            'pygments',
            ],

        scripts=['bin/ds_upload.py',
                 'bin/ds_status.py',
                 'bin/ds_download.py',
                    ],
        zip_safe=False)
