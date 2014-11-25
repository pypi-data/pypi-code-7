from setuptools import setup, find_packages

setup(
    name='digimat.gapi',
    version='0.1.8',
    description='Digimat Google API tools',
    namespace_packages=['digimat'],
    author='Frederic Hess',
    author_email='fhess@splust.ch',
    license='PSF',
    packages=find_packages('src'),
    package_dir = {'':'src'},
    install_requires=[
        'gspread',
        'strict_rfc3339',
        'httplib2',
        'google-api-python-client',
        'setuptools'
    ],
    dependency_links=[
        ''
    ],
    zip_safe=False)
