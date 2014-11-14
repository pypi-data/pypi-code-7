from distutils.core import setup

binpath = r"/usr/local/bin"
iconpath = r"/usr/share/icons/PopupBubble"

setup(
    name = "PopupBubble",
    packages = ["PopupBubble"],
    version = "0.0.9",
    data_files = [(binpath, ["scripts/pop_bubble.py", "scripts/pop_tk.py"])],
    description = "Cross-platform desktop notification using Qt",
    author = "Kaiyin Zhong",
    author_email = "kindlychung@gmail.com",
    url = "https://github.com/kindlychung/PopupBubble",
    keywords = ["notification", "cross-platform"]
    )

