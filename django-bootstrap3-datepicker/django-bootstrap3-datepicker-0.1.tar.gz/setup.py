from setuptools import setup


setup(
    name='django-bootstrap3-datepicker',
    packages=['bootstrap3_datepicker',],
    package_data={'bootstrap3_datepicker': ['static/bootstrap3_datepicker/css/*.css', 
                                          'static/bootstrap3_datepicker/js/*.js',
                                          'static/bootstrap3_datepicker/js/locales/*.js',]},
    include_package_data=True,
    version='0.1',
    description='Bootstrap3 compatible datepicker for Django projects.',
    long_description=open('README.rst').read(),
    author='James Hargreaves',
    author_email='james.hargreaves@qoobic.co.uk',
    url='https://github.com/qoobic/django-bootstrap3-datepicker.git',
    license='Apache License 2.0',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Environment :: Web Environment',
        'Framework :: Django',
    ],
)
