from setuptools import setup

setup(
    name='chain-sdk',
    version='1.0',
    author='Jonathan Warren',
    author_email='jonathan@coinapex.com',
    packages=['chain'],
    url='https://github.com/chain-engineering/chain-python',
    keywords='bitcoin',
    license='LICENSE',
    description='Official Python software development kit for the Chain.com API',
    long_description='Official Python software development kit for the Chain.com API',
    install_requires=[
        "requests >= 2.4.3",
        "python-bitcoinlib >= 0.2.1"
    ],
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        ],
)