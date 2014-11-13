__author__ = 'Ruben Nielsen'

import os
import subprocess
import hashlib

from Crypto import Random
from Crypto.Cipher import AES


class CallFailedError(Exception):
    pass


class Chdir:
    """
    A helper that lets you change the cwd environment variable temporarily.

    usage:

    with Chdir("/som/path"):
        # Do stuff
    """
    origin_path = ""
    cwd = ""

    def __init__(self, directory):
        self.origin_path = os.getcwd()
        self.cwd = directory

    def __enter__(self):
        os.chdir(self.cwd)
        return None

    def __exit__(self, type, value, traceback):
        os.chdir(self.origin_path)


class HelperMixin(object):
    """
    Contains a bunch of helpers to create better Operations
    """

    def call(self, command, accepted_return_codes=[0]):
        """
        Runs command and returns the output text and status code
        :param command: The command to be run
        :return: (output, status_code) tuple
        """
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        std_out, std_err = proc.communicate()
        return_code = proc.returncode

        if not return_code in accepted_return_codes or std_err:
            raise CallFailedError(
                'The command "%s" failed with return code: %s.\nAccepted return codes are %s\n\n%s' % (
                    command, return_code, accepted_return_codes, std_err
                )
            )
        return std_out, std_err, return_code

    def tar_folder(self, folder_path, tar_file, gzip=True):
        """
        Creates a tar archive with the given folder as its root.

        Imagine a folder structure like this

        foldera/
          folderb/
            file1.txt
          file2.txt

        if folderb is provided as the folder_path, the tar archive will include folderb as
        its root:

        folderb/
          file1.txt

        trailing slash is ignored.

        :param folder_path: The filepath to the folder you want to add to the new tar archive
        :param tar_file: The path to the tar archive, you want to create
        :param gzip: set to True, if you want to gzip the archive. Default is True
        :return: a tuple of (std_out, std_err, return_code) from the tar call
        """
        binary = "tar"
        opts = "cvf"

        # Remove trailing slash
        if folder_path[-1] == '/':
            folder_path = folder_path[:-1]
        i = folder_path.rfind('/')
        path, folder = folder_path[:i + 1], folder_path[i + 1:]
        if gzip:
            opts += "z"
        command = "%s %s %s %s" % (binary, opts, tar_file, folder)
        with Chdir(path):
            result = self.call(command)
        return result

    def untar_folder(self, tar_file, folder_path, gzip=True):
        """
        untars a tar archive. See tar_folder.

        :param tar_file: The path to the tar archive
        :param folder_path: The location you want the archive to be untared to
        :param gzip: set to True if the archive is gzipped. Default is True
        """
        binary = "tar"
        opts = "xvf"
        if gzip:
            opts += "z"
        command = "%s %s %s -C %s" % (binary, opts, tar_file, folder_path)
        return self.call(command)

    def is_iterable(self, obj):
        """
        Checks whether obj is an iterable

        :param obj: Any python object
        :return: True if obj is iterable
        """
        try:
            iter(obj)
        except TypeError:
            return False
        return True

    def remote_call(self, command, host):
        self.call("ssh %s '%s'" % (host, command))

    def create_perforce_checkpoint(self, source_path, host='', p4d_executable='p4d'):
        """
        Creates a checkpoint for the perforce server in the folder specified by
        source_path.

        :param source_path: The folder that contains your perforce files, and the location of the checkpoint
        :param p4d_executable: The path to the p4d executable
        """
        if not source_path[-1] == '/':
            source_path += '/'
        command = '%s -jc -z' % p4d_executable
        if host:
            self.remote_call("cd %s; %s" % (source_path, command), host=host)
        else:
            with Chdir(source_path):
                return self.call(command)

    def encrypt_file(self, in_filename, out_filename, passwd, chunk_size=8 * 1024):
        key = hashlib.md5(passwd.encode()).digest()
        iv = Random.get_random_bytes(16)
        crypto = AES.new(key, AES.MODE_CFB, iv)

        with open(in_filename, 'rb') as in_file:
            with open(out_filename, 'wb+') as out_file:
                out_file.write(iv)
                while True:
                    chunk = in_file.read(chunk_size)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += (' ' * (16 - len(chunk) % 16)).encode()
                    out_file.write(crypto.encrypt(chunk))

    def decrypt_file(self, in_filename, out_filename, passwd, chunk_size=8 * 1024):
        key = hashlib.md5(passwd.encode()).digest()
        with open(in_filename, 'rb') as in_file:
            with open(out_filename, 'wb+') as out_file:
                iv = in_file.read(16)
                crypto = AES.new(key, AES.MODE_CFB, iv)
                while True:
                    chunk = in_file.read(chunk_size)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        dec = crypto.decrypt(chunk).strip()
                    else:
                        dec = crypto.decrypt(chunk)
                    out_file.write(dec)

    def s3_sync(self, source, destination, aws_binary='aws'):
        if not destination.startswith('s3://'):
            self.call('mkdir -p %s' % destination)
        return self.call('%s s3 sync %s %s --recursive' % (aws_binary, source, destination))

    def download_website(self, url, destination):
        self.call('mkdir -p %s' % destination)
        with Chdir(destination):
            return self.call('''wget \\
                 --recursive \\
                 --no-clobber \\
                 --page-requisites \\
                 --html-extension \\
                 --convert-links \\
                 --restrict-file-names=windows \\
                 --domains wiki \\
                 --no-parent \\
                    %s''' % url)

    def rsync(self, source, destination, rsync_binary='rsync', extra_options='', accepted_return_codes=[0]):
        self.call('mkdir -p %s' % destination)
        self.call(
            "%s -rav %s %s %s" % (rsync_binary, extra_options, source, destination),
            accepted_return_codes
        )
