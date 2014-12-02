#!/usr/bin/env python
from setuptools import setup

setup(
    name="cocaine-pipeline-cli",
    version="0.11.9.4",
    author="Anton Tyurin",
    author_email="noxiouz@yandex.ru",
    maintainer='Anton Tyurin',
    maintainer_email='noxiouz@yandex.ru',
    description="Cocaine Tools for Cocaine Application Cloud.",
    long_description="CLI for cocaine-pipeline",
    license="LGPLv3+",
    platforms=["Linux", "BSD", "MacOS"],
    zip_safe=False,
    install_requires=["cocaine >= 0.11.1.0", "tornado", "simplejson"],
    namespace_packages=['cocaine'],
    entry_points={
        'console_scripts': [
            'cocaine-pipeline-cli = cocaine.pipeline:main',
        ]},
    packages=[
        "cocaine.pipeline",
    ],
    classifiers=[
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
    ],
)
