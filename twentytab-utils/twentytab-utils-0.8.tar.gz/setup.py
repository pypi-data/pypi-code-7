from setuptools import setup
import twentytab
setup(
    name='twentytab-utils',
    version=twentytab.__version__,
    author='20Tab S.r.l.',
    author_email='info@20tab.com',
    description='A django app that contains some utilities',
    url='https://github.com/20tab/twentytab-utils',
    packages=['twentytab'],
    license='MIT License',
    install_requires=[
        'Django',
    ],
)
