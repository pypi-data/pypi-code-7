from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='sparkprob',
    version='0.1',
    description='Sparklines for probability distributions',
    long_description=readme(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Science/Research',
    ],
    keywords='sparklines probability distribution print bar graph',
    url='https://github.com/ccorcos/sparkprob',
    author='Chet Corcos',
    author_email='ccorcos@gmail',
    license='MIT',
    packages=['sparkprob'],
    install_requires=[],
    test_suite='nose.collector',
    tests_require=['nose'],
    include_package_data=True,
    zip_safe=False
)
