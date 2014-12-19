from setuptools import setup

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='webpay',
    packages=['webpay'],
    version='2.2.2',
    author='webpay, tomykaira',
    author_email='administrators@webpay.jp, tomykaira@webpay.jp',
    url='https://webpay.jp',
    description='Bindings of WebPay API',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires=[
        'requests==2.2.1'
    ]
)
