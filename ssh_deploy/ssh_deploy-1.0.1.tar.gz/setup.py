from setuptools import setup

setup(
    name = "ssh_deploy",
    packages = ["ssh_deploy"],
    version = "1.0.1",
    install_requires=[
        "paramiko"
    ],
    description = "Automate tools for ssh deploy",
    author = "blueszhangsh",
    author_email = "blues.zhang.sh@gmail.com"
)
