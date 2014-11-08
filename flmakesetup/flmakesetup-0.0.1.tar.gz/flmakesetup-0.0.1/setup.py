from setuptools import setup, find_packages


with open("README.rst") as f:
    readme = f.read()

setup(
    name="flmakesetup",
    version="0.0.1",
    author="takahrio iwatani",
    author_email="taka.05022002@gmail.com",
    description="easy create setup.py",
    long_description=readme,
    url="https://github.com/float1251/flmakesetup",
    py_modules=["autosetup"],
    entry_points={
        "console_scripts":[
            "create-setuppy = autosetup:create_setuppy"
        ]
    }
)
