from distutils.core import setup
import os

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django_fotorama',
    version='0.001d',
    packages=['fotorama', 'fotorama.templatetags', 'fotorama.templates'],
    url='https://github.com/snznaota/django-fotorama',
    license='BSD',
    author='dezu',
    author_email='zhukovvitaliy@mail.ru',
    description='simple django-fotorama apps!'
)
