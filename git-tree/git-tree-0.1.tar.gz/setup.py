from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Topic :: Software Development",
]

setup(
    name='git-tree',
    description='List contents of git in a tree-like format',
    author='Kazufumi Onuma',
    author_email='k.o.system2@gmail.com',
    license='MIT License',
    url='https://github.com/kosystem/gitTree',
    version='0.1',
    packages=find_packages(),
    classifiers=classifiers,
    entry_points={
        'console_scripts': [
            'git-tree=gitTree.gitTree:main',
            ],
        }
    )
