from distutils.core import setup


setup(
    name='crosservice',
    version='0.2.5',
    packages=['crosservice'],
    install_requires=open('requirements.txt').read(),
    license='GPL',
    author='derfenix',
    author_email='derfenix@gmail.com',
    description='Gevent povered cross service communication tool',
    url='https://github.com/derfenix/crosservice',
    download_url='https://github.com/derfenix/crosservice/archive/v.0.2.5'
                 '.tar.gz',
    keywords=['communication', 'gevent', 'socket'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
    ],
)
