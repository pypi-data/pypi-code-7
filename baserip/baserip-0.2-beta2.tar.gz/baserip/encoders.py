from baserip.command import Command, Options

class Avconv(Command):
    def __init__(self, path, *args, **kwds):
        super().__init__(path, *args, **kwds)
        self.global_opts = Options()
        self.infile_opts = Options()
        self.map_opts = Options()
        self.video_opts = Options()
        self.audio_opts = Options()
        self.subt_opts = Options()
        self.format_opts = Options()
        self.outfile = None
        self.add_options(self.global_opts, self.infile_opts, self.map_opts, self.video_opts, 
            self.audio_opts, self.subt_opts, self.format_opts)
            
    def gen_command(self):
        command = super().gen_command()
        if self.outfile:
            command.append(self.outfile)
        return command
