from setuptools import setup

version='0.0.1' 

setup(
    name="pi_app",
  	description='A simple yet powerful tool for developing menu based apps',
  	version=version,
	author='Rodrigo Diez Villamuera',
	author_email='rodrigo@rodrigodiez.io',
	url='https://github.com/rodrigodiez/PiApp',
    download_url="https://github.com/rodrigodiez/PiApp/archive/%s.tar.gz" % (version),
    packages=['pi_app'],
    install_requires=['Adafruit_CharLCD>=1.0.0'],
    classifiers=[
		'Development Status :: 3 - Alpha',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2.7',
		'Topic :: Software Development'
    ]
)
