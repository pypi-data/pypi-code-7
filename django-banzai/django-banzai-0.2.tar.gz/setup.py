import os
from setuptools import setup, find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='django-banzai',
    version='0.2',
    license='MIT',
    description='Django API wrapper for mailing delivery '
                'service: http://get-n-post.ru/',
    long_description=read('README.rst'),
    keywords='mail email send wrapper api delivery django',
    url='https://github.com/saippuakauppias/django-banzai',
    author='Denis Veselov',
    author_email='progr.mail@gmail.com',
    include_package_data=True,
    packages=find_packages(),
    install_requires=['requests', 'lxml', 'django'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP'
    ],
)
