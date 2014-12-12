import sys
import json
import os.path
import subprocess
import re
import shlex

import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox

from . import tktool
from .tktool import error

from . import gui_root as _root
from . import to_marlowe
from . import defaultparam
from . import profile
from . import json_conv

from . import spawn_diag

import logging
logger = logging.getLogger(__name__)

from . import logconsole

def spawn_marlowe(master, marlowe_data_path):
    """spawn marlowe
    master, master Tk app or Frame
    marlowe_data_path path and filename for marlowe input data which
        includes '.dat' extension
    """
    profile_config = profile.load()

    bname = os.path.basename(marlowe_data_path)
    marlowe_workdir = os.path.dirname(marlowe_data_path)

    # usually marlowe in put data has .dat suffix
    # input argument is truncated .dat extension
    datext = re.compile(r'\.dat$')

    marlowe_input = datext.sub('', bname)

    # query setup marlowe 
    # command line which used previously
    # file dump succeeded, save lastdir in the profile
    marlowe_command = profile_config.get('marlowe_command', 'marlowe "{input}"')
    marlowe_shellexec = profile_config.get('marlowe_shellexec', True)

    query = spawn_diag.SpawnDialog(master, title='run marlowe program',
            cmdline=marlowe_command, input=marlowe_input, workdir=marlowe_workdir,
            shell=marlowe_shellexec)

    if query.result is not None:
        # save result
        profile_config['marlowe_command'] = query.result['command']
        profile_config['marlowe_shellexec'] = query.result['shellexec']
        profile.update(profile_config)

        # spawn program
        c = query.result['command'].format(input=marlowe_input)
        logger.info('executing: ' + c)
        p = subprocess.Popen(shlex.split(c),
                cwd=marlowe_workdir,
                shell=query.result['shellexec'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if stdout:
            logger.info(stdout)
        if stderr:
            logger.warn(stdout)
        logger.info('finished: ' + c)

def run():
    # test profile data
    try:
        profile_config = profile.load()
    except profile.Error as e:
        tkinter.messagebox.showerror('error on loding profile data', 'error on loding profile data.\n\n'+ e)
        sys.exit(2)
    except Exception as e:
        tkinter.messagebox.showerror('error on loding profile data', 'error on loding profile data.\n\n'+ str(e))
        sys.exit(2)

    app = tk.Tk()

    # setup gui
    root = _root.Root(app)

    root.pack(side=tk.TOP)

    menuframe = tk.Frame(app)

    pcol = 0

    def set_action():
        root.set(defaultparam.root_example)

    setbtn = tk.Button(menuframe, text='Set example', command=set_action)
    setbtn.grid(row=0, column=pcol, padx=5)
    pcol += 1

    def clear_action():
        root.clear()

    clearbtn = tk.Button(menuframe, text='Clear', command=clear_action)
    clearbtn.grid(row=0, column=pcol, padx=5)
    pcol += 1

    # get data and display on console
    def get_action():
        logger.info(root.get())

    getbtn = tk.Button(menuframe, text='Dump to Console', command=get_action)
    getbtn.grid(row=0, column=pcol, padx=5)
    pcol += 1

    def val_action():
        err = root.validate()
        if err:
            tktool.error.show_as_messagebox(err)

    valbtn = tk.Button(menuframe, text='Validate', command=val_action)
    valbtn.grid(row=0, column=pcol, padx=5)
    pcol += 1

    def load_action():
        profile_config = profile.load()
        fname = tkinter.filedialog.askopenfilename(title='Load json file',
                defaultextension='.json',
                initialdir=profile_config['lastdir'],
                filetypes=[('JSON', '*.json'), ('All', '*')])
        if fname:
            with open(fname, 'rt', encoding='utf-8') as stream:
                # load json format
                d = json.load(stream)

                # check version of data and solve it
                # d = context.solve_version(d)

                # translate json acceptable to native form
                d = json_conv.param_from_json(d)
                root.set(d)

                # load successed save lastdir
                profile_config['lastdir'] = os.path.dirname(fname)
                profile.update(profile_config)

    loadbtn = tk.Button(menuframe, text='Load .json', command=load_action)
    loadbtn.grid(row=0, column=pcol, padx=5)
    pcol += 1


    def save_action():
        class VExecption(Exception):
            def __init__(self, err):
                Exception.__init__(self)
                self.err = err

        try:
            err = root.validate()
            if err:
                raise VExecption(err)
            d = root.get()
        except VExecption as e:
            tkinter.messagebox.showerror('Validation error', 'validation error, save is aborted.\n\n'+tktool.error.format_errorstruct(e.err))
            return
        except Error as e:
            tkinter.messagebox.showerror('exception error', 'exception received, save is aborted.\n'+e)
            return

        profile_config = profile.load()

        fname = tkinter.filedialog.asksaveasfilename(
                title='Save MARLOWE input file',
                initialfile='*.dat',
                initialdir=profile_config['lastdir'],
                filetypes=[('MARLOWE input', '*.dat'), ('All', '*')])
        if fname:
            # add context version
            # d['version'] = context.currentversion

            # create json_name and jsont_name

            # 0. remove existing .json
            if fname[-len('.dat'):] == '.dat':
                json_name = fname[:-len('.dat')] + '.json'
            else:
                json_name = fname + '.json'
            jsont_name = json_name + '.t'

            if os.path.exists(json_name):
                os.unlink(json_name)

            # 1. dump .json.t

            with open(jsont_name, 'wt', encoding='utf-8') as stream: 
                d_json = json_conv.param_to_json(d)
                json.dump(d_json, stream, indent=2, sort_keys=True)

            # 2. save as marlowe data format 
            with open(fname, 'wt') as stream:
                to_marlowe.to_marlowe(d, stream)

            # 3. rename .json.temp to .json 
            os.rename(jsont_name, json_name)

            # file dump succeeded, save lastdir in the profile
            profile_config['lastdir'] = os.path.dirname(fname)
            profile.update(profile_config)

            spawn_marlowe(app, fname)

    getandsavebtn = tk.Button(menuframe, text='Save (& run)', command=save_action)
    getandsavebtn.grid(row=0, column=pcol, padx=5)

    menuframe.pack(side=tk.TOP)

    # logconsole
    logwin = logconsole.getLogConsoleWindow('marlowe_ui')

    app.mainloop()
