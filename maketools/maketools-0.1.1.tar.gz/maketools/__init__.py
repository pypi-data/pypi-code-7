import os

class Target(object):
    sh_build_commands = ()
    depends = ()
    always_build = False
    echo = False
    output = None

    def build(self, format_dict):
        self.format_dict = format_dict
        self.make_if_needs_making()

    def write_output(self):
        if self.output:
            basedir = os.path.dirname(self.output)
            if not os.path.exists(basedir):
                os.makedirs(basedir)

            with open(self.output, 'a'):
                os.utime(self.output, None)

    def make_if_needs_making(self, **kwargs):
        if self.always_build or not self.output or not os.path.exists(self.output):
            self.make(**kwargs)
            return 1 # Because we did build something
        else:
            files = []
            sub_depends = []

            for dep in self.depends:
                if type(dep) == str:
                    files.append(dep)
                elif issubclass(dep, Target):
                    sub_depends.append(dep)
                else:
                    raise Exception("Non String/Target dependency '%s' passed to configuration" % (dep,))
        
            needs_rebuild = False
            for f in files:
                if os.path.getmtime(self.output) < os.path.getmtime(f):
                    needs_rebuild = True
                    break
                    # One of the target files changed. rebuild.

            sub_status = []
            for SubTargetClass in sub_depends:
                subtarget = SubTargetClass()
                sub_status.append(subtarget.build(format_dict=self.format_dict))

            needs_rebuild = any(sub_status) | needs_rebuild
            if needs_rebuild:
                self.make(**kwargs)
                # A sub or file was rebuilt. We need to rebuild.

            # Tell parents that we did indeed rebuild.
            return needs_rebuild


    def make(self, **kwargs):
        self.py_build_commands(**kwargs)
        for line in self.sh_build_commands:
            line = line.format(**self.format_dict)
            if self.echo:
                print(line)
            os.system(line)

        self.write_output()

    def py_build_commands(self, **kwargs):
        pass

    def clean_command(self):
        pass