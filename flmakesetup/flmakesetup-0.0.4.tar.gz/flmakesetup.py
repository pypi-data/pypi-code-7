import os, sys
import urllib.request as req
from jinja2 import Environment, PackageLoader

username = os.getlogin()
path = os.getcwd()


def _input_required_value(message, default=None):
    """
    必須項目の入力
    """
    while True:
        val = input(message)
        if val:
            return val
        if default:
            return default
        print("Required Value...")


def _input_optional_value(message, default=None):
    """
    任意項目の入力
    """
    val = input(message)
    if val:
        return val
    if default:
        return default


def show_classifiers():
    """
    classifiersを表示する
    """
    res = req.urlopen("https://pypi.python.org/pypi?%3Aaction=list_classifiers")
    content = res.read()
    print(content.decode())


def create_setuppy():
    print("Start create setup.py")
    conf = {}
    conf["name"] = _input_required_value("name:")
    conf["version"] = _input_required_value("version:")
    conf["author"] = _input_required_value("auther(default={}):".format(username), default=username)
    conf["author_email"] = _input_optional_value("auther_email:")
    conf["test_suite"] = _input_optional_value("test_suite:")

    # 空白や改行の設定をする
    env = Environment(loader=PackageLoader("flmakesetup"), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template("setup.py")
    print(template.render(**conf))
    # fileをexportする
    global path
    p = os.path.join(path, "sample.py")
    if os.path.exists(p):
        print("setup.py already exist...", file=sys.stderr)
        return
    file = open(p, mode="w")
    file.write(template.render(**conf))

def main():
    if len(sys.argv)>1:
        arg = sys.argv[1]
    else:
        print("no suitable command...", file=sys.stderr)
        return
    if arg == "create-setuppy":
        create_setuppy()
    elif arg == "show-classifiers":
        show_classifiers()
    else:
        print("no suitable command...", file=sys.stderr)

if __name__ == "__main__":
    main()
