# -*- coding: utf-8 -*-
# Copyright (C)2014 DKRZ GmbH

"""Recipe r"""

import os
from mako.template import Template

from birdhousebuilder.recipe import conda

r_install_script = Template(
"""
% for pkg in pkg_list:
install.packages("${pkg}", dependencies = TRUE, repo="${repo}")
% endfor
"""
)

def install_pkgs(pkgs, repo, prefix):
    from subprocess import check_call
    from tempfile import NamedTemporaryFile

    pkg_list = conda.split_args(pkgs)
    if len(pkg_list) > 0:
        result = r_install_script.render(
            pkg_list=pkg_list,
            repo=repo
            )

        fp = NamedTemporaryFile(suffix='.R', prefix='install', delete=False)
        fp.write(result)
        fp.close()

        cmd = '%s/bin/R --no-save < %s' % (prefix, fp.name)
        check_call(cmd, shell=True)

        try:
            os.remove(fp.name)
        except OSError:
            pass

    return pkg_list

class Recipe(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        b_options = buildout['buildout']
        self.prefix = b_options.get('anaconda-home', conda.anaconda_home())

        self.repo = options.get('repo', "http://ftp5.gwdg.de/pub/misc/cran")
        self.pkgs = options.get('pkgs', '')
        self.on_update = conda.as_bool(options.get('on-update', 'false'))

    def install(self):
        self.execute()
        return tuple()

    def update(self):
        if self.on_update:
            self.execute()
        return tuple()

    def execute(self):
        #self.install_r()
        self.install_pkgs()

    def install_r(self):
        script = conda.Recipe(
            self.buildout,
            self.name,
            {'pkgs': 'r'})
        return script.install()
        
    def install_pkgs(self):
        return install_pkgs(self.pkgs, self.repo, self.prefix)
        
    
def uninstall(name, options):
    pass

