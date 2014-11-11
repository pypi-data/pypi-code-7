from distutils.core import setup

setup(
    name='django-ftp-deploy',
    version='2.0.0',
    author='Lukasz Pakula',
    author_email='lukaszpakula.pl@gmail.com',
    packages=[
        'ftp_deploy',
        'ftp_deploy.migrations',
        'ftp_deploy.models',
        'ftp_deploy.utils',
        'ftp_deploy.server',
        'ftp_deploy.server.forms',
        'ftp_deploy.server.templatetags',
        'ftp_deploy.server.views'
    ],
    include_package_data=True,
    url='https://github.com/lpakula/django-ftp-deploy',
    license='LICENSE.txt',
    description='Auto FTP deployment for django.',
    long_description=open('README.rst').read(),
    install_requires=[
        "pycurl == 7.19.5",
        "certifi == 0.0.8",
        "django-braces == 1.4.0",
        "django-crispy-forms==1.4.0",
        "celery==3.1.8"
    ],
)
