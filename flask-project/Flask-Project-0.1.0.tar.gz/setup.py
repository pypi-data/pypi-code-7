from setuptools import setup, find_packages
import flask_project

entry_points = {
    "console_scripts": [
        "flask-project = flask_project.command:main",
    ]
}

with open("requirements.txt") as f:
    requires = [l for l in f.read().splitlines() if l]

setup(
    name='Flask-Project',
    version=flask_project.__version__,
    packages=find_packages(),
    include_package_data=True,
    description='Flask project template generator.',
    long_description=open('README.rst').read(),
    url='https://github.com/hyperwood/Flask-Project',
    author='hyperwood',
    author_email='hyperwood.yw@gmail.com',
    license='MIT',
    keywords='flask sample template generator',
    install_requires=requires,
    entry_points=entry_points,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)