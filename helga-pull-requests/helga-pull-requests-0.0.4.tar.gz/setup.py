from setuptools import setup, find_packages

setup(
    name='helga-pull-requests',
    version='0.0.4',
    description='A helga plugin to quickly link to github pull requests.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        'Framework :: Twisted',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='helga github pull requests',
    author="Shaun Duncan",
    author_email="shaun.duncan@gmail.com",
    url="https://github.com/shaunduncan/helga-pull-requests",
    packages=find_packages(),
    py_modules=['helga_pull_requests'],
    include_package_data=True,
    zip_safe=True,
    entry_points=dict(
        helga_plugins=[
            'pull_requests = helga_pull_requests:pull_requests',
        ],
    ),
)
