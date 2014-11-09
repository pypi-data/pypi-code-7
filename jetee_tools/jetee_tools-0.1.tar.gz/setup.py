from setuptools import setup, find_packages


setup(
    name='jetee_tools',
    version=0.1,
    author='Sergey Dubinin',
    author_email='whackojacko.ru@gmail.com',
    install_requires=[
        u'pydns',
    ],
    packages=find_packages(),
    url='https://github.com/WhackoJacko/JeteeTools',
    classifiers=[],
)