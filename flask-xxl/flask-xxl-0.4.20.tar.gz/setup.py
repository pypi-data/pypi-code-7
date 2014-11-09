VERSION = '0,4,20'
from setuptools import setup, find_packages

def get_description():
    return open('README.txt','r').read()

def get_version():
    l,m,s = VERSION.split(',')
    return '{}.{}.{}'.format(l,m,s).strip()

config = dict(
        name='flask-xxl',
        version=get_version(),#'0.0.9',
        include_package_data=True,
        package_data = {
            '':['*.md','*.txt'],
        },
        author='Kyle Roux',
        author_email='kyle@level2designs.com',
        description='quick way to design large flask projects',
        long_description=get_description(),
        packages=find_packages(),
        package_dir={'':'.'},
        install_requires=[
            'flask==0.10.1',
            'flask-alembic==1.0.2',
            'flask-sqlalchemy==2.0',
            'flask-script==2.0.5',
            'flask-WTF==0.10.2',
            'jinja2==2.7.3',
            'LoginUtils==1.0.1',
            'Mako==1.0.0',
            'MarkupSafe==0.23',
            'SQLAlchemy==0.9.8',
            'WTForms==2.0.1',
            'Werkzeug==0.9.6',
            'alembic==0.6.7',
            'argparse==1.2.1',        
            'itsdangerous==0.24',
            'wsgiref==0.1.2',
            'six==1.8.0',
            'mr.bob2==0.2.3',
            ],
        zip_safe=False,
        entry_points=dict(
            console_scripts='flaskxxl-manage.py=flask_xxl.manage:main'
            ),
)

setup(**config)
