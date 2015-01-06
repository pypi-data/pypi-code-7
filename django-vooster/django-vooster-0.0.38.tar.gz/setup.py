from distutils.core import setup

setup(
	name='django-vooster',
	version='0.0.38',
	author='mufularo',
	author_email='bakagaidjin@gmail.com',
	packages=['django_vooster', 'django_vooster.templatetags'],
	license='Creative Commons Attribution-Noncommercial-Share Alike license',
	long_description=open('README').read(),
	#install_requires='django>1.5.1',
	url='http://mufularo.ru/',
	#classifiers=[
	#	'Framework :: Django',
	#	'Intended Audience :: Developers',
	#	'Operating System :: OS Independent',
	#	'Topic :: Software Development'
	#]
)
