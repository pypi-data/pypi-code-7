from setuptools import setup, find_packages


with open("README.rst") as f:
    readme = f.read()

setup(
    name="flmakesetup",
    version="0.0.8",
    author="takahrio iwatani",
    author_email="taka.05022002@gmail.com",
    description="easy create setup.py",
    long_description=readme,
    url="https://github.com/float1251/flmakesetup",
    py_modules=["flmakesetup"],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts":[
            "flmakesetup = flmakesetup:main"
        ]
    },
    install_requires=["Jinja2>=2.7.3"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
