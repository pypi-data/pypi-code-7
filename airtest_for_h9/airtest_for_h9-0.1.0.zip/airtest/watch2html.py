# -*- coding:utf-8 -*-

# *****************************************
# watch log to chart
#
# watch log Example:
# 17:44:42    17.0        67.1 MB     92.7 MB     385.8 MB    40.95 C     32.0 C      10.46 KB    92.09 KB
# 17:44:45    17.0        67.1 MB     92.8 MB     385.8 MB    41.19 C     32.0 C      10.46 KB    92.09 KB
#
# Author: Zheng wen
# Time  : 2014年12月18日 09:44:50
# *****************************************
import os
import sys
import shutil
import codecs
import pystache
from airtest import base

def render(logfile, htmldir):
    """
    parse logfile and render it to js file
    """
    if not os.path.exists(logfile):
        sys.exit('logfile: %s not exists' %(logfile))

    if not os.path.exists(htmldir):
        os.makedirs(htmldir)

    time_list = []
    cpu_list = []
    rss_list = []
    vss_list = []
    pss_list = []

    cpu_tem_list = []
    bat_tem_list = []

    up_list = []
    dw_list = []

    line_temp = []
    for line in open(logfile):
        line_temp = line.split()

        time_list.append(line_temp[0])

        cpu_list.append(float(line_temp[1]))
        pss_list.append(float(line_temp[2]))
        rss_list.append(float(line_temp[4]))
        vss_list.append(float(line_temp[6]))

        cpu_tem_list.append(float(line_temp[8]))
        bat_tem_list.append(float(line_temp[9]))
        up_list.append(float(line_temp[10]))
        dw_list.append(float(line_temp[11]))

    result = "x_time = " + str(time_list) + "\n" \
          + "cpu_list = " + str(cpu_list) + "\n" \
          + "pss_list = " + str(pss_list) + "\n" \
          + "rss_list = " + str(rss_list) + "\n" \
          + "vss_list = " + str(vss_list) + "\n" \
          + "cpu_tem_list = " + str(cpu_tem_list) + "\n" \
          + "bat_tem_list = " + str(bat_tem_list) + "\n" \
          + "up_list = " + str(up_list) + "\n" \
          + "dw_list = " + str(dw_list) + "\n"

    tmpldir = os.path.join(base.dirname(__file__), 'watchhtmltemplate')

    outpath = ""
    for name in os.listdir(tmpldir):
        fullpath = os.path.join(tmpldir, name)
        outpath = os.path.join(htmldir, name)
        if os.path.isdir(fullpath):
            shutil.rmtree(outpath, ignore_errors=True)
            shutil.copytree(fullpath, outpath)
            continue
        if fullpath.endswith('.swp'):
            continue
        content = open(fullpath).read().decode('utf-8')
        out = pystache.render(content, result)
        with open(outpath, 'w') as file:
            file.write(out.encode('utf-8'))

        # store json data file, for other system
        with open(os.path.join(htmldir, 'data.js'), 'w') as f:
            f.write(result.encode('utf-8'))

    # f = codecs.open(outpath + 'data.js', 'w+', 'utf-8')



# if __name__ == '__main__':
#     render('d:/18.txt', 'd:/18/')
