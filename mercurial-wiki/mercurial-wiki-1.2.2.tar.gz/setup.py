from distutils.core import setup

setup(
    name='mercurial-wiki',
    version='1.2.2',
    packages=['mercurial_wiki'],
    package_data={'mercurial_wiki': ['views/*', 'static/*']},
    scripts=['hgwiki.py'],
    url='https://bitbucket.org/brejoc/mercurial-wiki/',
    license='GPLv2',
    author='Jochen Breuer',
    author_email='brejoc@gmail.com',
    install_requires=[
        'bottle >= 0.11.6',
        'Jinja2 >= 2.6',
        'markdown2',
        'Mercurial'
    ],
    description='A developers wiki.',
    platforms='any',
)
