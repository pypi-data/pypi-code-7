from setuptools import setup
setup(
    author='Adam Matan',
    author_email='adam@matan.name',
    description='A python script for batch-pull git repos',
    license='MIT',
    name='gitpull',
    py_modules=['gitpull'],
    scripts=['gitpull'],
    url='https://github.com/adamatan/gitpull',
    version='0.2',
    install_requires=['termcolor', 'progressbar2', 'prettytable']
)
