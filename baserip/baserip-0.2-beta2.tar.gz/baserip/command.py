from baserip.utils import Singleton
import shutil

class CommandError(Exception):
    def __init__(self, command, errstr=''):
        self.command = command
        self.errstr = errstr
        
    def __str__(self):
        return '{}: {}'.format(self.command, self.errstr)

class CommandMissingError(CommandError):
    def __init__(self, command, errstr='Missing'):
        super().__init__(command, errstr)
        
    def __str__(self):
        return '{}: {}'.format(self.command, self.errstr)

class Options(list):
    def __init__(self, *args, sep=' '):
        args = ['0' if a == 0 else a for a in args]
        super().__init__(args)
        self._sep = sep
        
    def __str__(self):
        return self._sep.join([str(s) for s in self if s])

    def gen_options(self):
        return str(self).split()

class Command(object):
    def __init__(self, path, *args, **kwds):
        self.path = path
        self.options = Options(*args)
        
    def add_options(self, *args):
        self.options.extend(args)
      
    def gen_command(self):
        """
        Returns a list of strings which represent a subprocess command 
        suitable for feeding into :py:class:`subprocess.Popen` as the 
        *args* parameter.
        
        :return: list of strings
        :rtype: list
        """
        
        return [self.path] + self.options.gen_options()
    
    def __str__(self):
        return self.path + ' ' + str(self.options)

class Commands(object, metaclass=Singleton):
    def __init__(self, *command_list):
        self.commands = {}
        errlist = []
        for com in command_list:
            try:
                self.add_command(com)
            except CommandMissingError as err:
                errlist.append(err.command)
        if errlist:
            raise CommandError(errlist)
            
    def add_command(self, command, comclass=Command):
        path = shutil.which(command)
        if path:
            self.commands[command] = {'path': path, 'comclass': comclass}
        else:
            raise CommandMissingError(command,'Path to {} not found'.format(command))

    def register_command_class(self, com, comclass):
        try:
            self.commands[com]['comclass'] = comclass
        except KeyError:
            pass
            
    def make_command(self, command, *args, **kwargs):
        path = self.commands[command]['path']
        try:
            return self.commands[command]['comclass'](path, *args, **kwargs)
        except KeyError:
            return Command(path, *args, **kwargs)
            
    def __getattr__(self, attr):
        try:
            return self.commands[attr]['path']
        except KeyError:
            raise AttributeError(attr)
