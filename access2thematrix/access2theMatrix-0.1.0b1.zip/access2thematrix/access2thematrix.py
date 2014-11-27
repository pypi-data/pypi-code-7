# -*- coding: utf-8 -*-
#
#   Copyright © 2014 Stephan Zevenhuizen
#   access2theMatrix, (27-11-2014).
#

import os.path
import numpy as np
from struct import unpack
from time import localtime, strftime

class Im(object):

    def __init__(self):
        self.data = np.array([[]])
        self.width = 0
        self.height = 0
        self.y_offset = 0
        self.x_offset = 0
        self.angle = 0

class MtrxData(object):

    ALL_TRACES = np.array(['forward/up',   'backward/up',
                           'forward/down', 'backward/down'])

    def __init__(self):
        self.img_file_ident = 'ONTMATRX0101TLKB'
        self.par_file_ident = 'ONTMATRX0101ATEM'
        self.session = ''
        self.cycle = ''
        self.channel_name = ''
        self.raw_data = ''
        self.raw_param = ''
        self.param = {'BREF': ''}
        self.bricklet_size = 0
        self.data_item_count = 0
        self.data = np.array([])
        self.scan = None
        self.axis = None
        self.traces = np.array([])

    def _rotate_offset(self, centre, offset, angle):
        r_offset_x = offset[0] - centre[0]
        r_offset_y = offset[1] - centre[1]
        a = np.deg2rad(angle)
        x = r_offset_x * np.cos(a) - r_offset_y * np.sin(a) + centre[0]
        y = r_offset_x * np.sin(a) + r_offset_y * np.cos(a) + centre[1]
        offset = [x, y]
        return offset

    def _read_string(self, dp, data_block):
        dl = 4
        dln = unpack('<L', data_block[dp:dp + dl])[0]
        dp += dl
        dl = dln * 2
        return dp + dl, data_block[dp:dp + dl].decode('utf-16')

    def _read_data(self, dp, dp_plus, data_block):
        dl = 4
        dl += dp_plus
        id = data_block[dp + dp_plus:dp + dl]
        dp += dl
        if id == 'LOOB':
            dl = 4
            dpn = dp + dl
            data = bool(unpack('<L', data_block[dp:dpn])[0])
        elif id == 'GNOL':
            dl = 4
            dpn = dp + dl
            data = unpack('<l', data_block[dp:dpn])[0]
        elif id == 'BUOD':
            dl = 8
            dpn = dp + dl
            data = unpack('<d', data_block[dp:dpn])[0]
        elif id == 'GRTS':
            dpn, data = self._read_string(dp, data_block)
        return dpn, data

    def _scan_raw_param(self, dp, data):
        dl = 4
        id = data[dp:dp + dl]
        dp += dl
        dln = unpack('<L', data[dp:dp + dl])[0]
        dp += dl
        dl = dln
        if (id == 'REFX' or id == 'NACS' or id == 'TCID' or id == 'SCHC' or
            id == 'TSNI' or id == 'SXNC' or id == 'LNEG'):
            dp_plus = 0
            dl += 0
        else:
            dp_plus = 8
            dl += 8
        data_block = data[dp + dp_plus:dp + dl]
        if id == 'DPXE':
            dpb = 4
            i = 0
            len_data_block = len(data_block)
            while dpb < len_data_block:
                dpb, s = self._read_string(dpb, data_block)
                self.param[id[::-1] + '::s{0}'.format(i)] = s
                i += 1
        elif id == 'APEE':
            dpb = 8
            n_keys1 = unpack('<L', data_block[4:dpb])[0]
            for i in range(n_keys1):
                dpb, s = self._read_string(dpb, data_block)
                key1 = id[::-1] + '::{0}'.format(s)
                dlb = 4
                n_keys2 = unpack('<L', data_block[dpb:dpb + dlb])[0]
                dpb += dlb
                for j in range(n_keys2):
                    dpb, prop = self._read_string(dpb, data_block)
                    dpb, unit = self._read_string(dpb, data_block)
                    dpb, data = self._read_data(dpb, 4, data_block)
                    key = '{0}.{1}'.format(key1, prop)
                    self.param[key] = [data, unit]
        elif id == 'DOMP':
            dpb = 4
            dpb, eepa = self._read_string(dpb, data_block)
            dpb, prop = self._read_string(dpb, data_block)
            dpb, unit = self._read_string(dpb, data_block)
            dpb, data = self._read_data(dpb, 4, data_block)
            key1 = 'EEPA::{0}'.format(eepa)
            key = '{0}.{1}'.format(key1, prop)
            self.param[key] = [data, unit]
        elif id == 'YSCC':
            dpb = 4
            len_data_block = len(data_block)
            while dpb < len_data_block:
                dpb = self._scan_raw_param(dpb, data_block)
            self.param[id[::-1]] = ''
        elif id == 'TCID':
            dpb = 12
            n_keys = unpack('<L', data_block[8:dpb])[0]
            for i in range(n_keys):
                dpb += 16
                dpb, key = self._read_string(dpb, data_block)
                dpb, data = self._read_string(dpb, data_block)
            dlb = 4
            n_keys = unpack('<L', data_block[dpb:dpb + dlb])[0]
            dpb += dlb
            for i in range(n_keys):
                dpb += 4
                key = unpack('<L', data_block[dpb:dpb + dlb])[0]
                dpb += dlb + 8
                dpb, name = self._read_string(dpb, data_block)
                dpb, unit = self._read_string(dpb, data_block)
                self.param[id[::-1] + '::{0}'.format(key)] = [name, unit]
        elif id == 'REFX':
            dpb = 0
            dlb = 4
            len_data_block = len(data_block)
            while dpb < len_data_block:
                dpb += 4
                key1 = unpack('<L', data_block[dpb:dpb + dlb])[0]
                dpb += dlb
                dpb, name = self._read_string(dpb, data_block)
                dpb, unit = self._read_string(dpb, data_block)
                n_keys = unpack('<L', data_block[dpb:dpb + dlb])[0]
                dpb += dlb
                channel_parameters = {}
                for i in range(n_keys):
                    dpb, key2 = self._read_string(dpb, data_block)
                    dpb, data = self._read_data(dpb, 0, data_block)
                    channel_parameters[key2] = data
                self.param[id[::-1] + '::{0}'.format(key1)] = \
                                    [name, unit, channel_parameters]
        elif id == 'FERB':
            dpb = 4
            dpb, filename = self._read_string(dpb, data_block)
            self.param[id[::-1]] = filename
        else:
            self.param[id[::-1]] = ''
        return dp + dl

    def _scan_raw_data(self, dp, data):
        dl = 4
        id = data[dp:dp + dl]
        dp += dl
        dln = unpack('<L', data[dp:dp + dl])[0]
        dp += dl
        dl = dln
        if (id == 'CSED' or id == 'ATAD'):
            dp_plus = 0
            dl += 0
        else:
            dp_plus = 0
            dl += 8
        data_block = data[dp + dp_plus:dp + dl]
        if id == 'TLKB':
            dpb = 8
            secs = unpack('<Q', data_block[0:dpb])[0]
            self.param[id[::-1]] = strftime('%A, %d %B %Y %H:%M:%S',
                                            localtime(secs))
            dpb += 4
            len_data_block = len(data_block)
            while dpb < len_data_block:
                dpb = self._scan_raw_data(dpb, data_block)
        elif id == 'CSED':
            dlb = 4
            dpb = 20
            dpn = dpb + dlb
            self.bricklet_size = unpack('<i', data_block[dpb:dpn])[0]
            dpb = dpn
            dpn = dpb + dlb
            self.data_item_count = unpack('<i', data_block[dpb:dpn])[0]
        elif id == 'ATAD':
            fmt = '<%di' % self.data_item_count
            self.data = np.array(unpack(fmt, data_block))
        return dp + dl

    def _transfer(self, name, data, p):
        if name == 'TFF_Linear1D':
            r = (data - p['Offset']) / p['Factor']
        elif name == 'TFF_MultiLinear1D':
            r = (p['Raw_1'] - p['PreOffset']) * (data - p['Offset']) / \
                (p['NeutralFactor'] * p['PreFactor'])
        else:
            r = data
        return r

    def _data(self):
        keys = [k for k in self.param.iterkeys() if not k.find('DICT')]
        channel_name = self.channel_name.decode('utf-8')
        key = [k for k in keys if self.param[k][0] == channel_name][0]
        channel = self.param[key]
        key = 'XFER' + key[4:]
        axis_mirrored = [self.param['EEPA::XYScanner.X_Retrace'][0],
                         self.param['EEPA::XYScanner.Y_Retrace'][0]]
        xm = int(axis_mirrored[0])
        ym = int(axis_mirrored[1])
        xc = self.param['EEPA::XYScanner.Points'][0]
        yc = self.param['EEPA::XYScanner.Lines'][0]
        ylc = yc
        axis_length = [self.param['EEPA::XYScanner.Width'][0],
                       self.param['EEPA::XYScanner.Height'][0]]
        axis_offset = [self.param['EEPA::XYScanner.X_Offset'][0],
                       self.param['EEPA::XYScanner.Y_Offset'][0]]
        axis_clock_count_x = xc * (1 + xm)
        ytc = self.data_item_count // axis_clock_count_x
        if ytc <= yc:
            yc = ytc
            axis_mirrored[1] = False
        ym = int(axis_mirrored[1])
        z = self._transfer(self.param[key][0],
                           self.data[:axis_clock_count_x * ytc],
                           self.param[key][2])
        scan = np.empty(((1 + ym) * (1 + xm), yc, xc))
        z = np.reshape(z, (-1, xc))
        if axis_mirrored[0] and axis_mirrored[1]:
            scan[0] = z[:yc * 2:2]
            scan[1] = z[1:yc * 2:2][:, ::-1]
            scan[2, 2 * yc - ytc:] = z[yc * 2::2][::-1]
            scan[3, 2 * yc - ytc:] = z[yc * 2 + 1::2][::-1, ::-1]
        elif axis_mirrored[0] and not axis_mirrored[1]:
            scan[0] = z[:yc * 2:2]
            scan[1] = z[1:yc * 2:2][:, ::-1]
        elif not axis_mirrored[0] and axis_mirrored[1]:
            scan[0] = z[:yc]
            scan[1, 2 * yc - ytc:] = z[yc:][::-1]
        else:
            scan[0] = z
        axis = [[axis_offset[0], axis_length[0]],
                [axis_offset[1], axis_length[1]],
                [axis_mirrored[0], axis_mirrored[1], ylc, ytc],
                ['x', 'm', 'y', 'm']]
        if scan.shape[1] < 2 or scan.shape[2] < 2:
            scan = np.empty((1, 0, 0))
        return scan, axis

    def open(self, result_data_file):
        self.param = {'BREF': ''}
        self.bricklet_size = 0
        self.data_item_count = 0
        self.data = np.array([])
        try:
            last_part = result_data_file[result_data_file.rindex('--') + 2:]
            index_delimiter = [last_part.index('_'), last_part.index('.'),
                               last_part.rindex('_')]
            self.session = last_part[:index_delimiter[0]]
            self.cycle = last_part[index_delimiter[0] + 1:index_delimiter[1]]
            self.channel_name = last_part[index_delimiter[1] +
                                          1:index_delimiter[2]]
            result_file_chain = result_data_file[:result_data_file.rfind('--')]
            result_file_chain += '_0001.mtrx'
            f = open(result_data_file, 'rb')
            self.raw_data = f.read()
            f.close()
            f = open(result_file_chain, 'rb')
            self.raw_param = f.read()
            f.close()
        except:
            self.session = ''
            self.cycle = ''
            self.channel_name = ''
            self.raw_data = ''
            self.raw_param = ''
        id_img = self.raw_data[:len(self.img_file_ident)] == self.img_file_ident
        id_par = (self.raw_param[:len(self.par_file_ident)] ==
                  self.par_file_ident)
        filename = os.path.basename(result_data_file)
        f_name = filename.decode('utf-8')
        if id_img and id_par:
            try:
                dp = 12
                len_raw_param = len(self.raw_param)
                while dp < len_raw_param and self.param['BREF'] != f_name:
                    dp = self._scan_raw_param(dp, self.raw_param)
                dp = 12
                dp = self._scan_raw_data(dp, self.raw_data)
                error = False
            except:
                error = True
            if error:
                scan = None
                axis = None
                message = 'Error in data file ' + filename + '.'
            else:
                if '(' in self.channel_name:
                    scan = None
                    axis = None
                    message = 'Invalid data file ' + filename + '.'
                else:
                    try:
                        scan, axis = self._data()
                        if all(scan.shape):
                            message = 'Successfully opened and processed '\
                                      'data file ' + filename + '.'
                        else:
                            scan = None
                            axis = None
                            message = 'No data in data file ' + filename + '.'
                    except:
                        scan = None
                        axis = None
                        message = 'Error in processing data file ' + \
                                  filename + '.'
        else:
            scan = None
            axis = None
            message = 'Error in opening ' + filename + '.'
        self.scan = scan
        self.axis = axis
        if axis:
            i = np.array([True, axis[2][0], axis[2][1],
                          axis[2][0] and axis[2][1]])
            self.traces = self.ALL_TRACES[i]
            traces = dict(enumerate(self.traces))
        else:
            traces = {}
        return traces, message

    def select_image(self, trace):
        im = Im()
        if trace in self.traces:
            im.angle = self.param['EEPA::XYScanner.Angle'][0]
            im.width = self.axis[0][1]
            data = self.scan[list(self.traces).index(trace)]
            yc = data.shape[0]
            ylc = self.axis[2][2]
            ytc = self.axis[2][3]
            height = self.axis[1][1]
            x_offset = self.axis[0][0]
            y_offset = self.axis[1][0]
            centre = [x_offset, y_offset]
            if list(self.ALL_TRACES).index(trace) > 1:
                im.data = np.copy(data[2 * yc - ytc:])
                im.height =  height * (ytc - ylc - 1) / (ylc - 1)
                offset = [x_offset, y_offset + 0.5 * (height - im.height)]
            else:
                im.data = np.copy(data)
                im.height = height * (yc - 1) / (ylc - 1)
                offset = [x_offset, y_offset + 0.5 * (im.height - height)]
            if im.angle:
                offset = self._rotate_offset(centre, offset, im.angle)
            im.x_offset = offset[0]
            im.y_offset = offset[1]
            message = 'Trace ' + str(trace) + ' selected.'
        else:
            message = 'Error, ' + str(trace) + ' trace not available.'
        return im, message

