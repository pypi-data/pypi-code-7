from setuptools import setup

setup(
    name='pollywog',
    version=__import__('pollywog').__version__,
    description='pollywog',
    author='Charles Leifer',
    author_email='coleifer@gmail.com',
    url='http://github.com/coleifer/pollywog/',
    py_modules=['pollywog'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    test_suite='pollywog',
)
