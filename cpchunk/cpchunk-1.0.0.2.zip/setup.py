from setuptools import setup

setup(
    name='cpchunk',
    # NB: update cpchunk.py when changing this
    version='1.0.0.2',
    description="A tool for copying chunks of files",
    url='http://github.com/furrykef/cpchunk',
    author='Kef Schecter',
    author_email='furrykef@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Topic :: Utilities',
    ],
    scripts=['cpchunk.py']
)
