from os import path
import shutil


def _local_path(name):
    return path.join(path.dirname(__file__), name)


def install_headers(include_dir, package_name):
    """Install the headers of a known package_name into include_dir. Known
    package names are ['murmurhash', 'numpy'].

    >>> from os import path
    >>> my_include_dir = 'myenv/include/site'
    >>> path.exists(path.join(my_include_dir, 'numpy')) 
    False
    >>> install_headers(my_include_dir, 'numpy')
    >>> assert path.exists(path.join(my_include_dir, 'numpy')) # Dir created if not exists
    >>> assert path.isdir(path.join(my_include_dir, 'numpy'))
    >>> assert path.exists(path.join(my_include_dir, 'numpy', 'ndarray.h'))

    If instead:

    >>> path.exists(path.join(my_include_dir, 'numpy'))
    True

    install_headers will add any missing headers to the destination dir.
    """
    assert path.exists(include_dir) and path.isdir(include_dir)
    src_dir = _local_path(package_name)
    dest_dir = path.join(include_dir, package_name)
    if path.exists(dest_dir):
        for filename in os.listdir(src_dir):
            shutil.copy(path.join(src_dir, filename), path.join(dest_dir, filename))
    else:
        shutil.copytree(src_dir, dest_dir)
