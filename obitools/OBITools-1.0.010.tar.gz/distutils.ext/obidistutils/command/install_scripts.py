'''
Created on 20 oct. 2012

@author: coissac
'''

from distutils.command.install_scripts import install_scripts as ori_install_scripts
import os.path
from distutils import log

class install_scripts(ori_install_scripts):

    def initialize_options(self):
        ori_install_scripts.initialize_options(self)
        self.deprecated_scripts = None
        
    def revove_dot_py(self):
        for filename in self.get_outputs():
            pyfile = "%s.py" % filename
            if os.path.exists(pyfile):
                command = os.path.split(pyfile)[-1]
                log.info('Removing deprecated .py form of the unix command : %s (file %s)' % (command,pyfile))
                if not self.dry_run:
                    os.unlink(pyfile)
                try:
                    if not self.dry_run:
                        os.unlink(os.path.join(self.build_dir,command))
                except:
                    log.info('Unix command %s is not present in build dir' % command)
                    
    def remove_deprecated_script(self):
        
        if self.deprecated_scripts is not None:
            for f in self.deprecated_scripts:
                try:
                    ff = os.path.join(self.install_dir,f)
                    if not self.dry_run:
                        os.unlink(ff)
                    log.info('Removing deprecated unix command : %s (file : %s)' % (f,ff))
                    ff = os.path.join(self.build_dir,f)
                    if not self.dry_run:
                        os.unlink(ff)
                except:
                    log.info('Unix command %s is not present' % f)



    def run(self):
        self.remove_deprecated_script()
        ori_install_scripts.run(self)
        self.revove_dot_py()


