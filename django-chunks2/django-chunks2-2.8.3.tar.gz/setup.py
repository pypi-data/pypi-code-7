from setuptools import setup, find_packages

setup(
    name='django-chunks2',
    version='2.8.3',
    description='Keyed blocks of content for use in your Django templates',
    keywords="django chunks templates",
    author='Clint Ecker',
    author_email='me@clintecker.com',
    url='https://github.com/gotlium/django-chunks2',
    maintainer='gotlium',
    maintainer_email='gotlium@gmail.com',
    packages=find_packages(exclude=['demo']),
    include_package_data=True,
    package_data={'chunks': [
        'templates/chunks/*',
        'static/chunks/*',
        'locale/*/LC_MESSAGES/*'
    ]},
    install_requires=[
        'easy_thumbnails',
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Topic :: Utilities'
    ],
)
