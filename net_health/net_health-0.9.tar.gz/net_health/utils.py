import subprocess


class NovaManageExec:
    def __init__(self, exec_script_path):
        self.script = exec_script_path

    def call(self, check_exit_code=False):
        cmd = ['nova-manage', 'shell', 'script', self.script]
        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if check_exit_code and proc.returncode != 0:
            raise Exception("nova-manage exit status fail")
        return (out, proc.returncode)
