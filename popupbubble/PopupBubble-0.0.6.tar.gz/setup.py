from distutils.core import setup

import platform, os
sysname = platform.system()
if sysname == "Windows":
    binpath = os.getenv("SystemRoot")
else:
    binpath = r"/usr/local/bin"

setup(
    name = "PopupBubble",
    packages = ["PopupBubble"],
    version = "0.0.6",
    data_files = [(binpath, ["scripts/pop_bubble.py", "scripts/pop_tk.py"])],
    description = "Cross-platform desktop notification using Qt",
    author = "Kaiyin Zhong",
    author_email = "kindlychung@gmail.com",
    url = "https://github.com/kindlychung/PopupBubble",
    keywords = ["notification", "cross-platform"]
    )

