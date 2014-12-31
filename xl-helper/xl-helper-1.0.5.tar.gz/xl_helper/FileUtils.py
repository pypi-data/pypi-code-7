import inspect
import os
import shutil
from distutils import dir_util

class FileUtils:

    def __init__(self):
        pass


    @staticmethod
    def ensure_empty_dir(path):
        if os.path.exists(path) and (not os.path.isdir(path) or os.listdir(path) != []):
            raise Exception("Expected %s either not to exist or be an empty dir" % path)
        elif not os.path.exists(path):
            os.mkdir(path)

        return path

    @staticmethod
    def copy_subfolder(p1, p2, folder):
        p1_sub = os.path.join(p1, folder)
        if not os.path.isdir(p1_sub):
            return
        p2_sub = os.path.join(p2, folder)
        if not os.path.isdir(p2_sub):
            os.mkdir(p2_sub)
        dir_util.copy_tree(p1_sub, p2_sub)


    @staticmethod
    def create_dir_if_not_exists(path):
        if os.path.exists(path) and not os.path.isdir(path):
            raise Exception("Path % exists, but it is not a directory" % path)

        os.mkdir(path)

    @staticmethod
    def delete_dirs(*paths):
        for path in paths:
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)

    @staticmethod
    def delete_contents(location):
        for root, dirs, files in os.walk(location):
            for d in dirs:
                FileUtils.delete_dirs(os.path.join(root, d))
            for f in files:
                shutil.rmtree(os.path.join(root, f))

    @staticmethod
    def copy_contents(src, dst):
        if not os.path.isdir(src):
            return

        if not os.path.isdir(dst):
            os.mkdir(dst)

        for root, dirs, files in os.walk(src):
            for d in dirs:
                shutil.copytree(os.path.join(root, d), dst)
            for f in files:
                shutil.copyfile(os.path.join(root, f), os.path.join(dst, f))

    @staticmethod
    def move_contents(src, dst):
        if not os.path.isdir(src):
            return

        if not os.path.isdir(dst):
            os.mkdir(dst)

        for root, dirs, files in os.walk(src):
            for d in dirs:
                shutil.move(os.path.join(root, d), dst)
            for f in files:
                shutil.move(os.path.join(root, f), os.path.join(dst, f))

    @staticmethod
    def to_absolute_path(relative_path):
        return os.path.normpath(os.path.join(os.path.dirname(__file__), '..', relative_path))

    @staticmethod
    def proj_folder():
        cur_script_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        return os.path.split(cur_script_folder)[0]

    @staticmethod
    def conf_folder():
        return "{proj_dir}/conf".format(proj_dir=FileUtils.proj_folder())
