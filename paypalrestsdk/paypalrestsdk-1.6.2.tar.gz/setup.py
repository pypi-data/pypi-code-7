from distutils.core import setup

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'paypalrestsdk'))
from version import __version__

long_description="""
    The PayPal REST SDK provides Python APIs to create, process and manage payments.

    1. https://github.com/paypal/PayPal-Python-SDK/ - README and Samples
    2. https://developer.paypal.com/webapps/developer/docs/api/ - API Reference
  """

license='PayPal SDK License'
if os.path.exists('LICENSE.md'):
  license = open('LICENSE.md').read()

setup(
  name='paypalrestsdk',
  version= __version__,
  author='PayPal',
  author_email='DL-PP-PYTHON-SDK@ebay.com',
  packages=['paypalrestsdk'],
  scripts=[],
  url='https://github.com/paypal/PayPal-Python-SDK',
  license=license,
  description='The PayPal REST SDK provides Python APIs to create, process and manage payments.',
  long_description=long_description,
  install_requires=['requests', 'six', 'pyopenssl'],
  classifiers=[
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Topic :: Software Development :: Libraries :: Python Modules'
  ],
  keywords=['paypal', 'rest', 'sdk', 'payments', 'invoice', 'subscription', 'webhook']
)
