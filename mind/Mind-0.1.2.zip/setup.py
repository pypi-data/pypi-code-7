from distutils.core import setup

setup(name='Mind',
      version='0.1.2',
      author='Jakov Manjkas',
      author_email='jakov.manjkas@gmail.com',
      url='https://github.com/Knowlege/Mind',
      description='Mind is library for games in Python',
      keywords ='pygame game tiled tiledtmxloader',
      long_description="""\
Mind.Knowledge:\n
\tpart of library for data saving.\n
\tMind.Knowledge.Knowledge:\n
\t\tclass for all data in programm\n
\tMind.Knowledge.load:\n
\t\tfunction that loads saved data and returns Knowledge object\n
Mind.Orientation:\n
\tpart of library for maps.\n
\tMind.Orientation.MAP:\n
\t\tbasic map class\n
\tMind.Orientation.point:\n
\t\tbasic point class\n
\tMind.Orientation.group_of_points:\n
\t\tclass for group of points
""",
      packages = ['Mind'],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Intended Audience :: Developers',
          'Topic :: Games/Entertainment'
          ]
)
