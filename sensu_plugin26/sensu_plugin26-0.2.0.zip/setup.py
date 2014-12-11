from setuptools import setup
setup(
    name='sensu_plugin26',
    version='0.2.0',
    author='S. Zachariah Sprackett',
    author_email='zac@sprackett.com',
    packages=['sensu_plugin26', 'sensu_plugin26.test'],
    scripts=[],
    url='http://github.com/sensu/python_sensu_plugin/',
    license='LICENSE.txt',
    description='A framework for writing Python sensu plugins.',
    long_description="""
    """,
    install_requires=[
        'argparse'
    ],
    tests_require=[
        'pep8',
        'pylint'
    ],
)
