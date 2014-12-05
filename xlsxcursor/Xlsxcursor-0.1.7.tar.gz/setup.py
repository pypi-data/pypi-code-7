from setuptools import setup


VERSION = "0.1.7"

setup(
    name='Xlsxcursor',
    description="Xlsxcursor for xlsxwriter.",
    version=VERSION,
    url='https://github.com/KokocGroup/xslxcursor',
    download_url='https://github.com/KokocGroup/xslxcursor/tarball/v{}'.format(VERSION),
    packages=['xlsxcursor'],
    install_requires=[
        'xlsxwriter',
    ],
)
