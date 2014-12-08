from setuptools import setup, find_packages
import os.path


def get_file_contents_from_main_dir(filename):
    file_path = os.path.join('plonehrm', 'contracts', filename)
    this_file = open(file_path)
    contents = this_file.read().strip()
    this_file.close()
    return contents

history = get_file_contents_from_main_dir('HISTORY.txt')
readme = get_file_contents_from_main_dir('README.txt')
long = "%s\n\n\n%s" % (readme, history)


setup(name='plonehrm.contracts',
      version='3.10',
      description="Contracts for Plone HRM",
      long_description=long,
      classifiers=[
          "Framework :: Plone",
          "Framework :: Plone :: 3.3",
          "Framework :: Zope2",
          "Framework :: Zope3",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.4",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='human resource management contracts',
      author='Zest Software',
      author_email='info@zestsoftware.nl',
      url='https://prettigpersoneel.nl',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plonehrm'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.autopermission',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
