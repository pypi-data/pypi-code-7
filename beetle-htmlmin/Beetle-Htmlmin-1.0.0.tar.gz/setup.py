from setuptools import setup

setup(
    name='Beetle-Htmlmin',
    version='1.0.0',
    author='Jeppe Toustrup',
    author_email='jeppe@tenzer.dk',
    description='Enables Beetle to minimize HTML files',
    url='https://github.com/Tenzer/beetle-htmlmin',
    license='MIT',
    packages=[
        'beetle_htmlmin'
    ],
    install_requires=[
        'htmlmin',
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
