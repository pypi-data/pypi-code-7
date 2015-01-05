from setuptools import setup, find_packages

setup(
    name="act-bb-usage",
    version="1.0",
    url='https://github.com/lgp171188/act_bb_usage',
    license='GPLv3',
    description='''Fetch the total internet usage for the month
                   from ACT broadband portal''',
    author='L. Guruprasad',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['setuptools', 'requests'],
    entry_points={
        'console_scripts': ['act_bb_usage = act_bb_usage.usage:run'],
    },
    classifiers=[
        'Topic :: Utilities',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ]
)
