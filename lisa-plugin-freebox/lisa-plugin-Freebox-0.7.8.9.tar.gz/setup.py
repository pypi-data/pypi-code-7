from setuptools import setup
import json

metadata = json.loads(open('lisa/plugins/Freebox/freebox.json').read())

def listify(filename):
    return filter(None, open(filename, 'r').read().strip('\n').split('\n'))

if __name__ == '__main__':
    setup(
        version=metadata['version'],
        name='lisa-plugin-Freebox',
        packages=["lisa.plugins"],
        url='http://github.com/jfcjfc/LISA-PLUGINS-Freebox',
        license='MIT',
        author='jfcjfc',
        author_email='',
        description='LISA home automation system - Plugin',
        include_package_data=True,
        namespace_packages=['lisa'],
        install_requires=listify('requirements.txt'),
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )
