# coding=utf-8
import re
import json

re1 = re.compile(r"""
(?P<before_opening>(?:^|\n)[^\n%]*?)
(?P<env_opening>
  \$\$|
  \$|
  \\\(|
  \\\[|
  \\begin\ *?{(?P<env_name>
    (?:
      equation|align|math|displaymath|eqnarray|gather|flalign|multiline|alignat
    )
    \*?)}
)
(?P<env_content>
  (?:\n|\\\$|.)+?
)
(?(env_name)(?P<before_closing>(^|\n)[^\n%]*))
(?P<env_closing>
  \$|
  \\\]|
  \$\$|
  \\\]|
  \\\]|
  \\end\ *?{(?P=env_name)}
)
            """, re.VERBOSE)
s=r"""start$first$ second text $second$ third text
second line
as%daf\begin{align}
asdaf\begin{align}
aaa
asdasd\end{align}
sdf"""

# l=[s]
# print(l)

entries = []
match =re1.search(s)
while match:
    entry_text = {"type": "text", "content": s[:match.start()]+match.group("before_opening")}
    entry_math_env = {"type": "math_env",
                 "env_opening": match.group("env_opening"),
                 "env_content": match.group("env_content"),
                 "env_closing": match.group("env_closing")}
    entries.append(entry_text)
    entries.append(entry_math_env)
    s = s[match.end():]
    match =re1.search(s)
entries.append({"type": "text", "content": s})

print("entries", entries)
print("test")
print(json.dumps(entries, sort_keys=True, indent=4, separators=(',', ': ')))

    # before_opening = s[:match.start()]+match.group("before_opening")
    # new_entry.append([m.group("env_opening"), m.group("env_content"), m.group("env_closing")])
    # new_entry.append(ss[m.end():])
    # l.extend(new_entry)
    # print(l)
    # ss=l.pop()
    # m = re1.search(ss)




# l.append(ss[:m.start()]+m.group("before_opening"))
# l.append([m.group("env_opening"), m.group("env_content"), m.group("env_closing")])
# l.append(ss[m.end():])

# while m:
#     l.append(ss[:m.start()]+m.group("before_opening"))
#     l.append([m.group("env_opening"), m.group("env_content"), m.group("env_closing")])
#     l.append(ss[m.end():])
    # ss = l[-1]
    # print("ss:", ss)
    # m = re1.search(ss, m.end()+1)
# print(l)