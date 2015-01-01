from setuptools import setup


def readme():
    with open("README.rst") as f:
        f.read()

setup(name="vstat",
      version="0.1",
      description="Implementation of the v-statistic",
      url="https://github.com/dostodabsi/vstat.py",
      author="Fabian Dablander",
      author_email="dostodabsi@gmail.com",
      licence="MIT",
      packages=["vstat"],
      install_requires=["scipy"],
      include_package_data=True,
      test_suite="nose.collector",
      tests_require=["nose"],
      zip_safe=False)
