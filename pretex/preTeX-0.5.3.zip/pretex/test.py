import re
re1 = re.compile(r"""
\ \-\>
(?:
(?P<top>\^
  (?P<br>\{[^}]+?\})|
  (?P<fff>.+?\ )
)
|\ )
""", re.VERBOSE)

s=r"""a -> b
a ->^x b
a ->^a+1 b
a ->^{a+1} b"""
m = re1.match(s)
print(m)