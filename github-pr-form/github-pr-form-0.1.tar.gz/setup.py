import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name = 'github-pr-form',
    version = '0.1',
    author = 'Aaron N Browne',
    author_email = 'aaron0browne@gmail.com',
    url = 'https://github.com/aaron0browne/github-pr-form',
    description = 'A small python utility for generating forms from the command line and adding them to GitHub pull requests or issues, while tracking them in a secondary github repo.',
    long_description = long_description,
    download_url = 'httpd://github.com/aaron0browne/github-pr-form/tarball/v0.1',
    license = 'MIT License',
    keywords = ['github', 'rfc', 'change control', 'form', 'pull request'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Software Development :: Version Control'
    ],
    packages = find_packages(),
    install_requires = [
        'github3.py==0.9.3',
        'sh==1.09',
        'click==3.3',
        'markdown2==2.3.0',
        'selenium==2.44.0'
    ],
    entry_points = {
        'console_scripts': [
            'ghform = ghform.cli:cli'
        ]
    }
)
