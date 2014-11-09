from setuptools import setup

setup(
    name='jumprun',
    version='1.11',
    py_modules=['jumprun'],
    description='Unix CLI app for running scripts from any'
                ' directory in terminal',
    url='http://github.com/itsnauman/jumprun',
    author='Nauman Ahmad',
    author_email='nauman-ahmad@outlook.com',
    license='MIT',
    include_package_data=True,
    install_requires=[
        'termcolor',
        'docopt',
    ],
    entry_points='''
        [console_scripts]
        jr=jumprun:main
    ''',
)
