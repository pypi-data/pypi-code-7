from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='syncify',
    version='0.1',
    description='Wrap your asynchronous functions so they behave like synchronous function.',
    long_description=readme(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='async sync synchronous asynchronous',
    url='https://github.com/ccorcos/syncify',
    author='Chet Corcos',
    author_email='ccorcos@gmail',
    license='MIT',
    packages=['syncify'],
    install_requires=[],
    test_suite='nose.collector',
    tests_require=['nose'],
    include_package_data=True,
    zip_safe=False
)
