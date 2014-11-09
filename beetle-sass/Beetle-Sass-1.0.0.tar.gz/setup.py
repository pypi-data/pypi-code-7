from setuptools import setup

setup(
    name='Beetle-Sass',
    version='1.0.0',
    author='Jeppe Toustrup',
    author_email='jeppe@tenzer.dk',
    description='Enables Beetle to handle Sass files',
    url='https://github.com/Tenzer/beetle-sass',
    license='MIT',
    packages=[
        'beetle_sass'
    ],
    install_requires=[
        'libsass',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Markup',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
