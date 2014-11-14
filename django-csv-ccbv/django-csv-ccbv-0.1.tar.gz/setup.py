from setuptools import setup


setup(
    name='django-csv-ccbv',
    version = '0.1',
    description='Easy to fetch a CSV on a CCBV',
    author='aRkadeFR',
    author_email='contact@arkade.info',
    url='https://github.com/aRkadeFR/django-common-templatetags',
    package_dir = {'': 'src'},
    packages = ['csv_ccbv'],
    classifiers = [
        'Framework :: Django',
    ],
)
