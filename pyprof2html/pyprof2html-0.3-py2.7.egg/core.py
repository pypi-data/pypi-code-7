# -*- coding: utf-8 -*-
"""pyprof2html - Profile data convert to HTML.
"""

import codecs
import hashlib
import os
import re
import time
try:
    from hotshot import log, stats
except ImportError:
    pass # TODO: xxx
from pstats import Stats, func_std_string

import pyprof2html
from pyprof2html._compat import PY2
from pyprof2html.environment import CODEC, ENVIRON

__all__ = ['Converter']


def check_hotlinetimings(dump):
    """check to linetimings hotshot-profile datafile."""
    signature = "yes".encode()
    return True if dump.find(signature) > 0 else False


def check_hotshot(dump):
    """check to hotshot-profile datafile."""
    signature = "hotshot-version".encode()
    return True if dump.find(signature) > 0 else False


def check_cprofile(dump):
    """check to cProfile module's data or profile module's data."""
    signature = "sprof.Profiler".encode()
    return True if dump.find(signature) > 0 else False


def mapping_table(target, nall):
    levelmap = {0: '#ffffff',   # white
                #0: '#ccffcc',   # yellow green (light)
                1: '#66ff99',   # yellow green
                2: '#ffcc33',   # orange
                3: '#ff6666',   # pink
                4: '#ff3333',   # red
                }
    levels = [nall * 0.01, nall * 0.03, nall * 0.08, nall * 0.12, nall * 0.20]
    for level in range(len(levels)):
        if target < levels[level]:
            return levelmap[level]
    return levelmap[len(levelmap) - 1]


def detect_filecodec(lines):
    """detect to Python Source Code Encodings.

    Only strict check. see PEP 0263...
    """
    re_codec = re.compile("coding[:=]\s*([-\w.]+)")
    for cnt, line in enumerate(lines):
        if re_codec.search(line):
            return re_codec.findall(line)[0]
        if cnt >= 2:
            break
    return None


def convert_unit(float_number):
    """convert to unit of profile data.

    >>> convert_unit(0.12345)
    '123.5 [ms]'
    >>> convert_unit(0.12385)
    '123.9 [ms]'
    >>> convert_unit(0.12395)
    '124.0 [ms]'
    >>> convert_unit(0.0012395)
    '1.2 [ms]'
    >>> convert_unit(0.000012395)
    '12.4 [us]'
    >>> convert_unit(5)
    '5.000 [ s]'
    >>> convert_unit(5.9)
    '5.900 [ s]'
    >>> convert_unit(5.91)
    '5.910 [ s]'
    """
    if 1 > float_number >= 0.001:
        float_number = "%3.1lf [ms]" % (float_number * 1000)
    elif 0.001 > float_number >= 0.000001:
        float_number = "%3.1lf [us]" % (float_number * 1000000)
    elif 0.000001 > float_number >= 0.000000001:
        float_number = "%3.1lf [ns]" % (float_number * 1000000000)
    else:
        float_number = "%1.3lf [ s]" % float_number
    return float_number


def create_stylefile(output_directory):
    """create to style.css and jquery.js file"""
    for filename in ('style.css', 'jquery.js', 'jquery.tablesorter.min.js'):
        with open('%s/%s' % (output_directory, filename), 'wb') as fp:
            fp.write(ENVIRON.get_template(filename).render().encode(CODEC))
    filename = 'arrow.png'
    template_filename = 'arrow.png.base64'
    fp = open('%s/%s' % (output_directory, filename), 'wb')
    fp.write(ENVIRON.get_template(template_filename).render().encode())
    fp.close()

class Converter(object):
    """output to HTML from profile data
    """

    def __init__(self, filename):
        self.outfile = None
        self.output_dir = 'html'
        self.output_htmlfile = 'index.html'
        self.callers_htmlfile = 'callers.html'
        self.callers_data = []
        with open(filename, 'rb') as fp:
            dump = fp.read()
        self.tmpl = ENVIRON.get_template('main.html')
        self.callers_tmpl = ENVIRON.get_template('callers.html')
        if check_hotshot(dump[:20]):
            if not PY2:
                # TODO: xxx
                raise Exception('Not support for hotshot on Python3')
            self.prof = stats.load(filename)
            self.profile_datatype = "hotshot"
            if check_hotlinetimings(dump[102:108]):
                self.profline = log.LogReader(filename)
                self.tmplline = ENVIRON.get_template('hotshot-line.html')
                self.profile_datatype = "hotshot(line)"
        else:
            try:
                self.prof = Stats(filename)
            except ValueError as e:
                # TODO: xxx
                raise ValueError(filename)
            if check_cprofile(dump):
                self.profile_datatype = "cProfile"
            else:
                self.profile_datatype = "profile"
        self.filename = filename
        self.proftime = time.ctime(os.stat(filename).st_mtime)
        self.reporttime = time.ctime()
        self.outputtype = 'html'
        self.functions_number = 20
        self.profiledata_count = 0

    def _printhtml_source(self, filename, profs, outputfile):
        """printing one file profile line. return value is html render
        strings.
        """
        result = []
        if not os.path.exists(filename):
            return ""
        filecodec = detect_filecodec(open(filename).readlines())
        if filecodec is None:
            fileobj = open(filename)
        else:
            fileobj = codecs.open(filename, 'r', filecodec)
        for num, line in enumerate(fileobj, 1):
            if num in profs:
                result.append({'sec': profs[num]['sec'],
                               'cnt': profs[num]['cnt'],
                               'line': line})
            else:
                result.append({'sec': 'None', 'line': line})
        titletext = "pyprof2html - %s" % filename
        renderdict = {'title': titletext,
                      'proftime': self.proftime,
                      'reporttime': self.reporttime,
                      'filename': filename,
                      'profile_datatype': self.profile_datatype,
                      'version': pyprof2html.__version__,
                      'profdata': {'data': result,
                                   'totaltime': "%8.4lf" % self.prof.total_tt,
                                   'totalcalls': self.prof.total_calls}}
        if filecodec is None:
            outputfile.write(self.tmplline.render(renderdict))
        else:
            self.tmplline.stream(renderdict).dump(outputfile, CODEC)

    def _print_source(self, filename, profs):
        """printing one file profile line. return value is text strings.
        """
        result = []
        if not os.path.exists(filename):
            return ""
        result.append("=" * 60 + "\n")
        result.append(filename + "\n")
        result.append("=" * 60 + "\n")
        for num, line in enumerate(open(filename).readlines(), 1):
            if num in profs:
                result.append(" %3.4lfs | %7dn | %s" % (profs[num]['sec'],
                                                        profs[num]['cnt'],
                                                        line))
            else:
                result.append("         |          | %s" % (line))
        return ''.join(result)

    def _print_sources(self, profs):
        """wrapper of _print_source() and _printhtml_source() method.
        """
        ret = []
        sources = []
        info = {}
        filecnt = 0
        for i, prof in enumerate(profs):
            filename = prof[0]
            if (not sources.count(filename)) or (len(profs) == (i + 1)):
                if info != {}:
                    if self.outputtype == 'html':
                        out_filename = "%s/%s.html" % (self.output_dir,
                                       sources[filecnt].replace('/', '_'))
                        outputfile = open(out_filename, 'w')
                        self._printhtml_source(sources[filecnt],
                                               info, outputfile)
                        outputfile.close()
                    else:
                        ret.append(self._print_source(sources[filecnt], info))
                    filecnt += 1
                info = {}
                sources.append(filename)
            info[prof[1]] = {'sec': prof[2], 'cnt': prof[3]}
        return "".join(ret)

    def _analyze_profline(self):
        """analyzed to hotshot linetimings data.
        """
        profset = dict()
        for i in self.profline:
            if i[0] == 0 or i[0] == 1:  # WHAT_ENTER or WHAT_EXIT
                continue
            if i[1] not in profset:
                profset[i[1]] = [float(int(i[2]) / 1000000.), i[2]]
            else:
                profset[i[1]][0] += float(int(i[2]) / 1000000.)
                profset[i[1]][1] += i[2]
        profs = [(p[0], p[1], profset[p][0], profset[p][1]) for p in profset]
        profs.sort()
        return profs

    def _collect_callers_data(self, source, call_dict):
        """collect to similar of pstats.Stats.print_callers() data in
        self.callers_data.

        It refers to pstats.Stats.print_call_line() method.
        """
        clist = list(call_dict.keys())
        clist.sort()
        tempdata = []
        for cnt, func in enumerate(clist):
            name = func_std_string(func)
            value = call_dict[func]
            if isinstance(value, tuple):
                nc, cc, tt, ct = value
                del(cc)
            else:
                nc = value
                tt = self.prof.stats[func][2]
                ct = self.prof.stats[func][3]
            ncl = mapping_table(nc, self.prof.total_calls)
            ttl = mapping_table(tt, self.prof.total_tt)
            ctl = mapping_table(ct, self.prof.total_tt)
            if cnt:
                dst_function = ""
            else:
                dst_function = func_std_string(source)
            callers_link = hashlib.md5(func_std_string(source).encode()).hexdigest()
            tempdata.append({'dst_function': dst_function,
                             'callers_link': callers_link,
                             'ncalls': nc,
                             'ncallslevel': ncl,
                             'tottime': "%8.4f" % (tt),
                             'tottimelevel': ttl,
                             'cumtime': "%8.4f" % (ct),
                             'cumtimelevel': ctl,
                             'org_function': name})
        self.callers_data.append(tempdata)

    def _analyzed_prof(self):
        """analyzed to not linetimings profile data.
        """
        self.prof.sort_stats('time', 'calls')
        self.prof.stream = open(os.devnull, 'w')    # darty hack
        backstream = self.prof.stream
        funclist = self.prof.get_print_list(())[1]
        self.prof.stream = backstream
        self.prof.stream.close()
        datalist = list()
        self.profiledata_count = len(funclist)
        for cnt, func in enumerate(funclist):
            if cnt >= self.functions_number:
                break
            stat = self.prof.stats[func]
            ncalls = stat[0]
            if not int(ncalls):
                ## skip to 0calls function
                self.profiledata_count -= 1
                continue
            self._collect_callers_data(func, self.prof.stats[func][4])
            #tottime = convert_unit(stat[2])
            tottime = "%8.4lf" % stat[2]
            try:
                totpercall = "%8.4lf" % float(stat[2] / stat[0])
            except ZeroDivisionError:
                totpercall = "0.0000"
            cumtime = "%8.4lf" % stat[3]
            try:
                cumpercall = "%8.4lf" % float(stat[3] / stat[0])
            except ZeroDivisionError:
                cumpercall = "0.0000"
            ncallslevel = mapping_table(ncalls, self.prof.total_calls)
            tottlevel = mapping_table(stat[2], self.prof.total_tt)
            totclevel = mapping_table(float(totpercall), self.prof.total_tt)
            cumtlevel = mapping_table(stat[3], self.prof.total_tt)
            cumclevel = mapping_table(float(cumpercall), self.prof.total_tt)
            linelink = "%s.html" % func[0].replace('/', '_')
            callers_link = hashlib.md5(func_std_string(func).encode()).hexdigest()
            data = {
                'func': func,
                'linelink': linelink,
                'ncalls': ncalls,
                'tottime': tottime,
                'cumtime': cumtime,
                'totpercall': totpercall,
                'cumpercall': cumpercall,
                'ncallslevel': ncallslevel,
                'cumtimelevel': cumtlevel,
                'tottimelevel': tottlevel,
                'totcalllevel': totclevel,
                'cumcalllevel': cumclevel,
                'callers_link': callers_link,
            }
            datalist.append(data)
        profdata = {
            'totaltime': "%8.4lf" % self.prof.total_tt,
            'totalcalls': self.prof.total_calls,
            'data': datalist,
        }
        return profdata

    def _hookraw(self):
        """hook rawtext print
        """
        if self.profile_datatype == 'hotshot(line)':
            profs = self._analyze_profline()
            print(self._print_sources(profs))
        else:
            self.prof.sort_stats('time', 'calls')
            self.prof.print_stats()

    def _hookhtml(self):
        """hook html print
        """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        filepath = "%s/%s" % (self.output_dir, self.output_htmlfile)
        self.outfile = open(filepath, 'w')
        profdata = self._analyzed_prof()
        titletext = "pyprof2html - %s" % self.filename
        create_stylefile(self.output_dir)
        if self.profile_datatype == 'hotshot(line)':
            profs = self._analyze_profline()
            self._print_sources(profs)
        self.outfile.write(
            self.tmpl.render(title=titletext,
                             proftime=self.proftime,
                             reporttime=self.reporttime,
                             profdata=profdata,
                             profiledata_count=self.profiledata_count,
                                  thisname=self.output_htmlfile,
                             version=pyprof2html.__version__,
                             profile_datatype=self.profile_datatype))
        self.outfile.close()
        filepath = "%s/%s" % (self.output_dir, self.callers_htmlfile)
        self.outfile = open(filepath, 'w')
        render_data = dict(title=titletext,
                           proftime=self.proftime,
                           reporttime=self.reporttime,
                           profile_datatype=self.profile_datatype,
                           callers_data=self.callers_data,
                           profdata=profdata,
                           profiledata_count=self.profiledata_count,
                           thisname=self.callers_htmlfile,
                           version=pyprof2html.__version__)
        self.outfile.write(
            self.callers_tmpl.render(render_data))
        self.outfile.close()

    def printout(self, filetype='html', output_directory='html',
                 output_htmlfile='index.html', functions_number=20):
        """print to html or text.
        """
        self.outputtype = filetype
        self.output_dir = output_directory
        self.output_htmlfile = output_htmlfile
        self.functions_number = functions_number
        if filetype == 'raw':
            self._hookraw()
        else:
            self._hookhtml()
