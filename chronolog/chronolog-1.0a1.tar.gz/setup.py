from distutils.core import setup
setup(name='chronolog',
      description='Time tracking application for unix platforms',
      author='Bart Riepe',
      author_email='bart@chronolog.us',
      url='https://www.chronolog.us',
      version='1.0a1',
      include_package_data=True,
      packages=["chronolog"],
      install_requires=['unirest'],
      entry_points = {
        "console_scripts": [
            # modify script_name with the name you want use from shell
            # $ script_name [params]
            "chronolog = chronolog.chronolog:start",
        ],
    }
      )
