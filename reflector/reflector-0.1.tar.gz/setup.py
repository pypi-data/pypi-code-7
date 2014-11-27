from setuptools import setup, find_packages

setup(
    name='reflector',
    version='0.1',
    description='TCP connection reflector',
    author='Soren Hansen',
    author_email='Soren.Hansen@ril.com',
    url='http://github.com/sorenh/reflector',
    license='Apache 2.0',
    keywords='tcp network monitoring',
    py_modules=['reflector'],
    entry_points={
        'console_scripts': [
            'reflector = reflector:main',
        ],
    },
)
