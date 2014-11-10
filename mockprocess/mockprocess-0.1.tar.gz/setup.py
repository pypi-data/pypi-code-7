from setuptools import setup

__version__ = '0.1'

__desc__ = 'Mocks for subprocess commands'

if __name__ == '__main__':
    setup(
        name="mockprocess",
        version=__version__,
        description=__desc__,
        py_modules=['mockprocess', 'test_mockprocess'],
        zip_safe=True,
        install_requires=['nose'],
        include_package_data=True,
        url='https://bitbucket.org/rw_grim/mockprocess',
        author='Gary Kramlich',
        author_email='grim@reaperworld.com',
    )
