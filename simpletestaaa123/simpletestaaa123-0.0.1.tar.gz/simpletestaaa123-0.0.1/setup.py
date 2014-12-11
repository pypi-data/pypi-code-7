from setuptools import setup, find_packages

setup(
    name = 'simpletestaaa123',
    version = '0.0.1',
    keywords = ('simple', 'test'),
    description = 'just a simple test',
    license = 'MIT License',
    install_requires = ['jieba','mmh3'],

    author = 'zhaorr',
    author_email = 'not@all.com',

    packages = find_packages(),
    platforms = 'any',
)

