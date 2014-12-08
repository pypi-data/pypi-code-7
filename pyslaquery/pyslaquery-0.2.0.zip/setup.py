from distutils.core import setup

setup(
    name="pyslaquery",
    version="0.2.0",
    description="A really simple wrapper around Slack API, for querying information from Slack channels and users.",
    author="@haukurk",
    author_email="haukur@hauxi.is",
    packages=["pyslaquery"],
    install_requires=["requests"],
    url='https://github.com/haukurk/pyslaquery',
    download_url='https://github.com/haukurk/pyslaquery/releases/tag/v0.2.0',
    keywords=['slack', 'channels', 'query'],
    classifiers=[]
)