from distutils.core import setup

setup(name='Mind',
      version='0.1.3.1',
      author='Jakov Manjkas',
      author_email='jakov.manjkas@gmail.com',
      url='https://github.com/Knowlege/Mind',
      description='Mind is library for games in Python',
      keywords ='pygame game tiled tiledtmxloader',
      long_description="""\
Mind.Knowledge:\n
\tpart of library for data saving.\n
\tMind.Knowledge.data_bytes:\n
\t\tfunction that data(number, string...) converts to bytes\n
\tMind.Knowledge.Knowledge:\n
\t\tclass for all data in programm\n
\tMind.Knowledge.bytes_data:\n
\t\tfunction that bytes converts to data(numbers, strigns...)\n
\tMind.Knowledge.load:\n
\t\tfunction that loads saved data and returns Knowledge object\n
Mind.Orientation:\n
\tpart of library for maps.\n
\tMind.Orientation.MapError:\n
\t\texception for points outside the map
\tMind.Orientation.MAP:\n
\t\tbasic map class\n
\tMind.Orientation.point:\n
\t\tbasic point class\n
\tMind.Orientation.group_of_points:\n
\t\tclass for group of points
\tMind.Orientation.rect:\n
\t\tbacis map rect class\n
\tMind.Orientation.tiled_map (only if tiledtmxloader can be imported):\n
\t\tclass for map in tiled\n
Mind.Test\n
\tpart of library for testing other parts (it just helps people to get library)\n
\tMind.Test.test_know:\n
\t\ttest Mind.Knowledge.Knowledge\n
\tMind.Test.test_load:\n
\t\ttest Mind.Knowledge.load (test_know must be runed first!)\n
\tMind.Test.test_map:\n
\t\ttest Mind.Orientation.MAP and other map objects\n
\tMind.Test.test_tiled_map:\n
\t\ttest Mind.Orientation.tiled_map
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
