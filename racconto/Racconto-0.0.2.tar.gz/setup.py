from distutils.core import setup

setup(
    name='Racconto',
    version='0.0.2',
    # FIXME: walk directories instead of hard coding package names
    packages=['racconto','racconto.hooks'],
    license='MIT',
    long_description='Static blog generator',
    url='http://github.com/avidity/racconto',
    author='Felix Panozzo (Avidity)',
    author_email='code@avidity.se',
    install_requires = [
        "Jinja2 >=2.6",
        "PyYAML >= 3.10",
        "markdown2 >= 2.1.0",
        "mock >= 1.0.1",
    ],
)
