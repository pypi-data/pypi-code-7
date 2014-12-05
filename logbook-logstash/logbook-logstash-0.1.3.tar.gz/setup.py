# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='logbook-logstash',
    version='0.1.3',
    author='Darío Blanco Iturriaga',
    author_email='dario@darioblanco.com',
    packages=['logbook_logstash'],
    scripts=[],
    url='https://github.com/sharkerz/logbook-logstash/',
    license='LICENSE',
    description='JSON logstash formatter for logbook',
    long_description=open('README.rst').read(),
    zip_safe=False,
)
