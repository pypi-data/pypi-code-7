#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import subprocess
import time
import urllib
import json
import threading

import airtest
import click
import humanize
from airtest import log2html as airlog2html
from airtest import watch2html as watchlog2html
from airtest import androaxml

__debug = False


def _wget(url, filename=None):
    print 'DOWNLOAD:', url, '->', filename
    return urllib.urlretrieve(url, filename)


def _run(*args, **kwargs):
    if __debug:
        click.echo('Exec: %s [%s]' %(args, kwargs))
    kwargs['stdout'] = kwargs.get('stdout') or sys.stdout
    kwargs['stderr'] = kwargs.get('stderr') or sys.stderr
    p = subprocess.Popen(args, **kwargs)
    p.wait()


def _get_apk(config_file, cache=False):
    apk = None
    if os.path.exists(config_file):# compatiable with cli-1
        with open(config_file) as file:
            cfg = json.load(file)
            apk = cfg.get('apk')
            if not apk:
                apk = cfg.get('android', {}).get('apk_url') 
    
    if not apk:
        apk = raw_input('Enter apk path or url: ')
        assert apk.lower().endswith('.apk')
        # FIXME: save to file
        with open(config_file, 'wb') as file:
            file.write(json.dumps({'apk': apk}))

    if re.match('^\w{1,2}tp://', apk):
        if cache and os.path.exists('tmp.apk'):
            return 'tmp.apk'
        _wget(apk, 'tmp.apk')
        apk = 'tmp.apk'
    return apk

@click.group()
@click.option('-v', '--verbose', is_flag=True, help='Show verbose information')
def cli(verbose=False):
    global __debug
    __debug = verbose

@cli.command(help='Get package and activity name from apk')
@click.argument('apkfile', type=click.Path(exists=True))
def inspect(apkfile):
    pkg, act = androaxml.parse_apk(apkfile)
    click.echo('Package Name: "%s"' % pkg)
    click.echo('Activity: "%s"' % act)

@cli.command(help='Convert airtest.log to html')
@click.option('--logfile', default='log/airtest.log', help='airtest log file path',
              type=click.Path(exists=True, dir_okay=False), show_default=True)
@click.option('--listen', is_flag=True, help='open a web server for listen')
@click.option('--port', default=8800, help='listen port', show_default=True)
@click.argument('outdir', type=click.Path(exists=False, file_okay=False))
def log2html(logfile, outdir, listen, port):
    airlog2html.render(logfile, outdir)
    if listen:
        click.echo('Listening on port %d ...' % port)
        _run('python', '-mSimpleHTTPServer', str(port), cwd=outdir)

@cli.command(help='Convert watch.log to html')
@click.option('--logfile', help='watch log file path',
              type=click.Path(exists=True, dir_okay=False), show_default=True)
@click.option('--listen', is_flag=True, help='open a web server for listen')
@click.option('--port', default=8880, help='listen port', show_default=True)
@click.argument('watchdir', type=click.Path(exists=False, file_okay=False))
def watch2html(logfile, watchdir, listen, port):
    if logfile:
        watchlog2html.render(logfile, watchdir)
        if listen:
            click.echo('Listening on port %d ...' % port)
            _run('python', '-mSimpleHTTPServer', str(port), cwd=watchdir)
    else:
        click.echo("Can not find watch_log_file, you should specify th watch_log_file!")


@cli.command(help='Take a picture of phone')
@click.option('--phoneno', help='If multi android dev connected, should specify serialno')
@click.option('--platform', default='android', type=click.Choice(['android', 'windows', 'ios']), show_default=True)
@click.option('--out', default='snapshot.png', type=click.Path(dir_okay=False),
        help='out filename [default: "snapshot.png"]', show_default=True)
def snapshot(phoneno, platform, out):
    try:
        app = airtest.connect(phoneno=phoneno, device=platform)
        app.takeSnapshot(out)
    except Exception, e:
        click.echo(e)

@cli.command(help='Install apk to phone')
@click.option('--no-start', is_flag=False, help='Start app after successfully installed')
@click.option('--conf', default='air.json', type=click.Path(dir_okay=False), help='config file', show_default=True)
@click.option('-s', '--serialno', help='Specify which android device to connect')
@click.argument('apk', required=False)
def install(no_start, conf, serialno, apk):
    apk = _get_apk(conf)

    adbargs = ['adb']
    if serialno:
        adbargs.extend(['-s', serialno])
    args = adbargs + ['install', '-r', apk]
    # install app
    _run(*args)

    if no_start:
        return
    pkg, act = androaxml.parse_apk(apk)
    args = adbargs + ['shell', 'am', 'start', '-n', pkg+'/'+act]
    _run(*args)

@cli.command(help='Uninstall package from device')
@click.option('--conf', default='air.json', type=click.Path(dir_okay=False), help='config file')
@click.option('-s', '--serialno', help='Specify which android device to connect')
@click.argument('apk', required=False)
def uninstall(conf, serialno, apk):
    if not apk:
        apk = _get_apk(conf, cache=True)
    pkg, act = androaxml.parse_apk(apk)
    args = ['adb']
    if serialno:
        args.extend(['-s', serialno])
    args += ['uninstall', pkg]
    _run(*args)

@cli.command(help='Watch cpu, mem')
@click.option('--conf', default='air.json', type=click.Path(dir_okay=False), help='config file', show_default=True)
@click.option('-p', '--package', default=None, help='Package name which can get by air.test inspect, this is conflict with --conf')
@click.option('-n', '--interval', default=3, show_default=True, help='Seconds to wait between updates')
@click.option('-s', '--serialno', help='Specify which android device to connect')
@click.option('-h', '--human-readable', is_flag=True, help='Print size with human readable format')
@click.option('-o', '--output-file', type=click.Path(dir_okay=False), help='Save output to file(no title)')
def watch(conf, package, interval, serialno, human_readable, output_file):
    if not package:
        apk = _get_apk(conf, cache=True)
        package, _ = androaxml.parse_apk(apk)

    app = airtest.connect(devno=serialno, device=airtest.ANDROID, monitor=False)

    pid = app.dev.set_pid(package)

    ps_pid = app.dev.get_ps_pid(package)


    bat_time = app.dev.get_bat(ps_pid)

    # print app.dev.getdevinfo()
    out_fd = None
    if output_file:
        out_fd = open(output_file, 'w')

    # thread.start_new_thread(app.dev.console_show, ())
    #
    if output_file:
        threading.Thread(target = app.dev.get_fps, args = (output_file + ".fps", True)).start()
    else:
        threading.Thread(target = app.dev.get_fps, args = (output_file, False)).start()

    mem_items = ['PSS', 'RSS', 'VSS']
    tem_items = [u'CPU', u"BAT"]
    dat_items = ['UPLOAD', 'DOWNLOAD']
    bat_items = ['BAT_TIME']


    items = ['TIME', 'CPU'] + mem_items + tem_items + dat_items + bat_items
    format = '%-12s'*len(items)
    print format % tuple(items)
    while True:
        time_start = time.time()
        values=[]
        values.append(time.strftime('%H:%M:%S'))
        
        cpu = app.dev.getCpu(package)
        values.append(str(cpu))

        mem = app.dev.getMem(package)
        for item in mem_items:
            v = int(mem.get(item))*1024
            if human_readable:
                v = humanize.naturalsize(int(v))
            values.append(str(v))

        tem = app.dev.get_tem()
        values.append(str(tem[0]))
        values.append(str(tem[1]))

        dat = app.dev.get_dat(pid)
        values.append(str(dat[0]))
        values.append(str(dat[1]))

        bat = app.dev.get_bat(ps_pid) - bat_time
        values.append(str(bat))

        print format % tuple(values)

        if out_fd:
            out_fd.write((format + '\n') % tuple(values))
            out_fd.flush()

        sleep = interval - (time.time() - time_start)
        if sleep > 0:
            time.sleep(sleep)

@cli.command(help='Run GUI in browser')
@click.option('--workdir', default=os.getcwd(), type=click.Path(file_okay=False), help='working directory')
@click.option('-s', '--serialno', help='Specify which android device to connect')
@click.option('--reload', default=False, is_flag=True, help='For developer to auto reload code when code change')
def gui(workdir, serialno, reload):
    from . import webgui
    os.environ['WORKDIR'] = workdir
    import webbrowser
    webbrowser.open('http://localhost:5000')
    webgui.serve(use_reloader=reload)


def main():
    cli()

if __name__ == '__main__':
    main()

################################################################

# if __name__ == '__main__':
#     try:
#         main()
#     except KeyboardInterrupt:
#         print 'Exited by user'
