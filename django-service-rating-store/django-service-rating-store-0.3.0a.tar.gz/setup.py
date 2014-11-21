from setuptools import setup, find_packages

setup(
    name="django-service-rating-store",
    version="0.3.0a",
    url='https://github.com/praekelt/django-service-rating-store',
    license='BSD',
    description=(
        "Django app that allows storage and visualisation of Service Rating data posted via REST API"),
    long_description=open('README.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='devops@praekeltfoundation.org',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django',
        'django-tastypie',
        'South',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
    ],
)
