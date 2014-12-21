import os
class Target(object):
    """
    A representation of a target to build. 

    :var sh_build_commands: A tuple of strings containing terminal commands to be executed
                            line by line by the system to make this target.
    :var depends:   A tuple containing either of: filepaths (string) or
                    sub build classes (subclass Target). 
                    Allows for having recursive requirements.
    :var always_build:  A boolean determing whether to always build the project (default: False)
    :var echo:  echo sh_build_commands as they are executed line by line. (default: False)
    :var output:    A file which the target will create. Used to determine if 
                    a target needs updating by comparing this file's modification
                    date/time to the modification time of any requirements. If a file is not 
                    provided, the target will be built every time. (default: None)

    """

    sh_build_commands = ()
    depends = ()
    always_build = False
    echo = False
    output = None

    def build(self, format_dict):
        """
        Build this target.

        :param format_dict: A dictionary of keys/values which will be used to 
                            format strings given to sh_build_commands.
        """
        self.format_dict = format_dict
        return self.make_if_needs_making()

    def write_output(self):
        """
        If an output file is specified for the target, touch the file
        so we can compare when building next time and determine if the 
        target needs to be re-made.
        """
        if self.output:
            basedir = os.path.dirname(self.output)
            if not os.path.exists(basedir):
                os.makedirs(basedir)

            with open(self.output, 'a'):
                os.utime(self.output, None)

    def make_if_needs_making(self, **kwargs):
        """
        Recursively check if the target needs to be re-made. 
        Checks whether any required files have changed since last
        build and also checks if any dependent targets need rebuilding.
        """

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
        """
        Run the scripts to build the target.
        Then touch the output file.
        """

        self.py_build_commands(**kwargs)
        for line in self.sh_build_commands:
            line = line.format(**self.format_dict)
            if self.echo:
                print(line)
            os.system(line)

        self.write_output()

    def py_build_commands(self, **kwargs):
        """
        A stub for python build commands. A python function which 
        can be implemented to perform python code instead of shell 
        code for build commands. Python build commands will be 
        executed BEFORE shell commands.   
        """
        pass

    def clean_command(self):
        """
        Execute the clean command for this target.
        """
        pass