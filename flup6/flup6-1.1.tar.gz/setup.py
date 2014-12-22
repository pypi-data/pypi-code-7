from setuptools import setup, find_packages
setup(
    name = 'flup6',
    version = '1.1',
    packages = find_packages(),
    zip_safe = True,
    
    entry_points = """
    [paste.server_runner]
    ajp = flup.server.paste_factory:run_ajp_thread
    fcgi = flup.server.paste_factory:run_fcgi_thread
    scgi = flup.server.paste_factory:run_scgi_thread
    ajp_thread = flup.server.paste_factory:run_ajp_thread
    fcgi_thread = flup.server.paste_factory:run_fcgi_thread
    scgi_thread = flup.server.paste_factory:run_scgi_thread
    ajp_fork = flup.server.paste_factory:run_ajp_fork
    fcgi_fork = flup.server.paste_factory:run_fcgi_fork
    scgi_fork = flup.server.paste_factory:run_scgi_fork
    """,
    
    author = 'Mikhail Denisenko',
    author_email = 'denisenkom@gmail.com',
    description = 'Random assortment of WSGI servers',
    license = 'BSD',
    url='https://bitbucket.org/denisenkom/flup',
    classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
    'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    )
