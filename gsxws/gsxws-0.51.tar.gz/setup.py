from setuptools import setup, find_packages

setup(
    name="gsxws",
    version="0.51",
    description="Library for communicating with GSX Web Services API.",
    install_requires=['PyYAML', 'lxml'],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP"
    ],
    keywords="gsx, python",
    author="Filipp Lepalaan",
    author_email="filipp@fps.ee",
    url="https://github.com/filipp/py-gsxws",
    download_url="https://github.com/filipp/py-gsxws/tarball/0.51",
    license="BSD",
    packages=find_packages(),
)
