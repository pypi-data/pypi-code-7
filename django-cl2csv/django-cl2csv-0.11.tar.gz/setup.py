from setuptools import setup, find_packages


setup(name='django-cl2csv',
      version='0.11',
      description='Export what you see in the Django admin list view.',
      author='Scott Meisburger',
      author_email='smeisburger@gmail.com',
      url='https://github.com/protonpopsicle/django-cl2csv',
      packages=find_packages(),
      license = 'GPLv3',
      keywords = 'django csv export')
