class Registry:
    def all(self):
        """TODO: get this from a web service if we ever need this functionality later."""
        units = """
4145dd1d
d2a593fd
a6fb75a5
0f29fb21
92c85574
07cf535f
02590a8f
83e7a9af
67a9beea
ad2a5920
91017f38
7d80598c
a593f39d
164fce20
73d4df5e
880bf969
5903ca41
9a593f26
aa593f26
5a54b241
e40f29fe
c329ab35
5b73e921
29bedd42
"""
        return set(units.splitlines())
