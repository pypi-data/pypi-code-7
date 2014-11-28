from setuptools import setup, find_packages
import tab_translation

setup(name='twentytab-tab-translation',
      version=tab_translation.__version__,
      description='A django app to apply jQuery UI tab view to translated modeltranslation fields',
      author='20tab S.r.l.',
      author_email='info@20tab.com',
      url='https://github.com/20tab/twentytab-tab-translation',
      license='MIT License',
      install_requires=[
          'Django >=1.6',
          'django-appconf>=0.6',
          'django-modeltranslation'
      ],
      packages=find_packages(),
      include_package_data=True,
      package_data={
          '': ['*.html', '*.css', '*.js', '*.gif', '*.png', ],
      }
)
