import os
import sys
import subprocess
from argparse import ArgumentParser
import urllib.request as req
from jinja2 import Environment, PackageLoader
import pip

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


def show_classifiers(args):
    """
    classifiersを表示する.
    """
    res = req.urlopen("https://pypi.python.org/pypi?%3Aaction=list_classifiers")
    content = res.read()
    print(content.decode(), end="")


def create_setuppy(args):
    """
    setup.pyを生成する.
    """
    print("Start create setup.py")
    conf = {}
    conf["name"] = _input_required_value("name:")
    conf["version"] = _input_required_value("version:")
    conf["author"] = _input_required_value(
        "author(default={}):".format(username),
        default=username
    )
    conf["author_email"] = _input_optional_value("author_email:")
    conf["test_suite"] = _input_optional_value("test_suite:")

    # 空白や改行の設定をする
    env = Environment(
        loader=PackageLoader("flmakesetup"),
        trim_blocks=True,
        lstrip_blocks=True
    )
    template = env.get_template("setup.tmpl")
    print(template.render(**conf))
    # fileをexportする
    global path
    p = os.path.join(path, "setup.py")
    if os.path.exists(p):
        print("setup.py already exist...", file=sys.stderr)
        return
    file = open(p, mode="w")
    file.write(template.render(**conf))


def setup_test_environment(args):
    """
    testに必要なライブラリ等をinstallする.
    """
    # coverageをinstallする
    dist_list = pip.get_installed_distributions()
    if not any(["coverage" in dist.project_name for dist in dist_list]):
        subprocess.call("pip install coverage", shell=True)
    else:
        print("Already install coverage")

    # flake8をinstallする
    if not any(["flake8" in dist.project_name for dist in dist_list]):
        subprocess.call("pip install flake8", shell=True)
    else:
        print("Already install flake8")


def main():

    parser = ArgumentParser()
    sub_parser = parser.add_subparsers()

    # settings create
    create_parser = sub_parser.add_parser("create", help="create setup.py")
    create_parser.set_defaults(func=create_setuppy)

    # setttings show-classifiers
    show_parser = sub_parser.add_parser(
        "show-classifiers",
        help="show classifiers list"
    )
    show_parser.set_defaults(func=show_classifiers)

    # setup test-env
    test_env_parser = sub_parser.add_parser(
        "setup-test-env",
        help="setup test environment"
    )
    test_env_parser.set_defaults(func=setup_test_environment)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.parse_args(["-h"])


if __name__ == "__main__":
    main()
