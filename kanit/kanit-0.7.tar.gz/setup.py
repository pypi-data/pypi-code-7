from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='kanit',
        version='0.7',
        description='Kanit kanban tool',
        url='https://github.com/LazarusID/kanit',
        author='Clay Dowling',
        author_email='clay@lazarusid.com',
        license='BSD',
        packages=['kanit'],
        scripts=['bin/kanit'],
        zip_safe=False)


