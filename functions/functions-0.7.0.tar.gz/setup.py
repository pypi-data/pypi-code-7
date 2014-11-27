from setuptools import setup


__version__ = "0.7.0"


setup(
    name='functions',
    version=__version__,
    description='Functional programming in Python',
    author='Charles Reese',
    author_email='charlespreese@gmail.com',
    url='https://github.com/creese/functions',
    download_url=(
        'https://github.com/creese/functions/archive/' + __version__ + '.zip'
    ),
    py_modules=('functions',)
)
