# -*- coding: utf-8 -*-
import subprocess
import pkg_resources


class Notifier(object):

    NOTIFIER_BASE_CMD = '"{cmd}"{img_arg}{img}{add_args} {msg_arg} "{msg}"'

    def __init__(self, cmd, msg_arg, img_arg='', add_args=''):
        self._cmd = cmd
        self._msg_arg = msg_arg
        self._img_arg = self._prepare_arg(img_arg)
        self._add_args = self._prepare_arg(add_args)
        self._ok_img = self._prepare_resource_arg(img_arg, pkg_resources.resource_filename(__name__, 'images/ok.png'))
        self._nok_img = self._prepare_resource_arg(img_arg, pkg_resources.resource_filename(__name__, 'images/nok.png'))

    def _prepare_arg(self, arg):
        return '' if arg == '' else ' {}'.format(arg)

    def _prepare_resource_arg(self, arg, resource_path):
        return '' if arg == '' else ' "{}"'.format(resource_path)

    def send_ok(self, name):
        cmd = self._build_ok_call(name)
        subprocess.Popen(cmd, shell=True)

    def send_nok(self, name):
        cmd = self._build_nok_call(name)
        subprocess.Popen(cmd, shell=True)

    def _build_ok_call(self, name):
        return self.NOTIFIER_BASE_CMD.format(cmd=self._cmd,
                                             img_arg=self._img_arg,
                                             img=self._ok_img,
                                             add_args=self._add_args,
                                             msg_arg=self._msg_arg,
                                             msg=name)

    def _build_nok_call(self, name):
        return self.NOTIFIER_BASE_CMD.format(cmd=self._cmd,
                                             img_arg=self._img_arg,
                                             img=self._nok_img,
                                             add_args=self._add_args,
                                             msg_arg=self._msg_arg,
                                             msg=name)
