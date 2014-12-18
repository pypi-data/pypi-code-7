from setuptools import setup

setup(
    name='pycrates',
    version='1.0beta',
    packages=['pycrates'],
    author='Jimmy Shen',
    author_email='thejimmyshen@gmail.com',
    summary='Python object serialization library',
    description='Easily package your object state for storage or transmission.',
    keywords=['serialization'],
    license='MIT',
    install_requires=['python-dateutil>=2.3'],
    test_suite='tests',
    url='https://github.com/jimmyshen/pycrates',
    download_url='https://github.com/jimmyshen/pycrates/tarball/1.0beta',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License'
    ]
)
