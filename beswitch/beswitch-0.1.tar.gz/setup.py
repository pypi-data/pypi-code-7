import setuptools


configuration = {
    "name": "beswitch",
    "version": "0.1",
    "description": "Backend switch for Python packages",
    "classifiers": [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    "keywords": "backend frontend facade adaptor",
    "url": "https://bitbucket.org/thoughteer/beswitch",
    "author": "Iskander Sitdikov",
    "author_email": "thoughteer@gmail.com",
    "license": "MIT",
    "packages": ["beswitch"],
    "install_requires": [],
    "zip_safe": False
}
setuptools.setup(**configuration)
