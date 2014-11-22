from setuptools import setup

setup(
    name='twotter',
    version='0.1.0',
    description='Scrapes BAS Air Unit asset locations',
    long_description=__doc__,
    url='https://github.com/kenners/twotter',
    author='Kenrick Turner',
    author_email='kenrickturner@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='scraping json antarctica aircraft latitude',
    packages=['twotter'],
    install_requires=[
        'simplejson>=3.5.2',
        'requests>=2.4.3',
        'basemap>=1.0.7',
        'matplotlib>=1.3.1',
        'numpy>=1.8.1'
    ],
    package_data={
        'twotter': ['twotter.json'],
    },
    entry_points={
        'console_scripts': [
            'twotter_snapshot=twotter:main'
        ],
    },
)
