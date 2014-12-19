from PyQt4.QtGui import (QGroupBox, QComboBox, QLineEdit, QSpinBox, QRegExpValidator, 
    QDialog, QFormLayout, QDialogButtonBox, QProgressBar,QPalette, QColor, QHBoxLayout, 
    QPushButton, QCheckBox, QLabel, QTreeView)
from PyQt4.QtCore import QRegExp, pyqtSlot, Qt, pyqtSignal
from io import StringIO
from collections import deque
from baserip.command import Commands, Options
from threading import Thread
from collections import Counter
import subprocess as subp
import re

def _generate_codecs():
    maxlen = 60
    codecs = subp.check_output(('avconv', '-codecs'), stderr = subp.DEVNULL, 
        universal_newlines=True)
    acodec_dict = {}
    vcodec_dict = {}
    recodec = re.compile(
        r'^.E(?P<ctype>[AV]).{3}\W+(?P<ext>\w+)\W+(?P<desc>(\w+\W+)+)')
    with StringIO(codecs) as codecs:
        for codec in codecs:
            match = recodec.search(codec)
            if match:
                desc = match.group('desc')[:-1]
                encpos = desc.find('(encoder')
                if encpos >= 0:
                    desc = desc[:encpos].strip()
                decpos = desc.find('(decoder')
                if decpos >= 0:
                    desc = desc[:decpos].strip()
                desc = desc[:maxlen]
                if match.group('ctype') == 'A':
                    # nasty hack
                    acodec_dict[desc] = match.group('ext') == 'vorbis' and 'libvorbis' or match.group('ext')
                elif  match.group('ctype') == 'V':
                    vcodec_dict[desc] = match.group('ext')
    acodec_dict['Copy'] = vcodec_dict['Copy'] = 'copy'
    return acodec_dict, vcodec_dict

_audio_codecs, _video_codecs = _generate_codecs()

class BitrateValidator(QRegExpValidator):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRegExp(QRegExp(r'\d+(\.\d+)?[yzafpnumcdhkKMGTPEZY]?'))

class SpinBox(QSpinBox):
    def __init__(self, value=0, parent=None):
        super().__init__(parent)
        self.setRange(0, 999999)
        self.setValue(value)

class H264Dialog(QDialog):
    def __init__(self, parent=None, retval=None):
        super().__init__(parent)
        self.setWindowTitle('H264 Profile')
        profiles = ('baseline', 'main', 'high', 'high10', 'high422', 'high444')
        presets = ('ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 
            'slow', 'slower', 'veryslow', 'placebo')
        tunes = ('film', 'animation', 'grain', 'stillimage', 'psnr', 'ssim', 'fastdecode',
            'zerolatency')
        layout = QFormLayout()
        
        self.cbo_profiles = QComboBox(self)
        self.cbo_profiles.addItems(profiles)
        try:
            index = profiles.index(retval['-profile'])
        except:
            index = 2
        self.cbo_profiles.setCurrentIndex(index)
        layout.addRow('Profile:', self.cbo_profiles)
        
        self.cbo_presets = QComboBox(self)
        self.cbo_presets.addItems(presets)
        try:
            index = presets.index(retval['-preset'])
        except:
            index = 5
        self.cbo_presets.setCurrentIndex(index)
        layout.addRow('Preset:', self.cbo_presets)
        
        self.cbo_tunes = QComboBox(self)
        self.cbo_tunes.addItems(tunes)
        try:
            index = tunes.index(retval['-tune'])
        except:
            index = 0
        self.cbo_tunes.setCurrentIndex(index
        )
        layout.addRow('Tune:', self.cbo_tunes)
        
        bbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)
        layout.addRow(bbox)
        
        self.returnval = retval
        
        self.setLayout(layout)
        
    def accept(self):
        self.returnval = {
            '-profile': self.cbo_profiles.currentText(), 
            '-preset': self.cbo_presets.currentText(), 
            '-tune': self.cbo_tunes.currentText()
        }
        super().accept()
        
    def reject(self):
        self.returnval = None
        super().reject()

class CodecGroup(QGroupBox):
    def __init__(self, title, ctype, stream, parent, checked=False):
        super().__init__(title, parent)
        self.codec_type = ctype
        self.stream = stream
        self.setCheckable(True)
        self.setChecked(checked)
        self.codec_extra = None
        
    def make_map_opt(self):
        map_parm = ''
        if self.codec_type == 'video':
            map_parm = Options('v', 0, sep=':')
        elif self.codec_type == 'audio' or self.codec_type == 'subtitle':
            map_parm = Options('i', self.stream.streamid, sep=':')
        return Options('-map', map_parm)
        
class SubtitleGroup(CodecGroup):
    def __init__(self, title, stream, parent, checked=False):
        super().__init__(title,'subtitle', stream, parent, checked)
        inner_layout = QFormLayout()
        inner_layout.addRow('Language:', QLabel(stream.language))
        self.scodec_combo = SubtitleCombo()
        inner_layout.addRow('Codec:', self.scodec_combo)
        self.setLayout(inner_layout)
        
    def make_subt_opts(self, stream_num):
        subt_opts = Options()
        codec_opt = Options('-codec', stream_num, sep=':')
        subt_opts.append(codec_opt)
        subt_opts.append(self.scodec_combo.codecs[self.scodec_combo.currentText()])
        return subt_opts
        
class AudioGroup(CodecGroup):
    def __init__(self, title, stream, parent, checked=False):
        super().__init__(title,'audio', stream, parent, checked)
        inner_layout = QFormLayout()
        inner_layout.addRow('Language:', QLabel(stream.language))
        inner_layout.addRow('Format:', QLabel(stream.format))
        inner_layout.addRow('Channels:', QLabel(str(stream.channels)))
        self.acodec_combo = AudioCombo()
        inner_layout.addRow('Codec:', self.acodec_combo)
        self.bitrate_edit = BitrateLineEdit('128k')
        inner_layout.addRow('Bitrate:', self.bitrate_edit)
        self.setLayout(inner_layout)

    def make_audio_opts(self, stream_num):
        audio_opts = Options()
        codec_opt = Options('-codec', stream_num, sep=':')
        audio_opts.append(codec_opt)
        audio_opts.append(_audio_codecs[self.acodec_combo.currentText()])
        if self.acodec_combo.currentText() != 'Copy':
            bitrate_opt = Options('-b', stream_num, sep=':')
            audio_opts.append(Options(bitrate_opt, self.bitrate_edit.text()))
        audio_opts.extend((Options('-strict', stream_num, sep=':'), 'experimental'))
        return audio_opts
        
class VideoGroup(CodecGroup):
    cropdata = pyqtSignal(tuple)

    def __init__(self, title, stream, parent, checked=False):
        super().__init__(title,'video', stream, parent, checked)
        inner_layout = QFormLayout()
        inner_layout.addRow('Length:', QLabel(str(stream.length)))
        inner_layout.addRow('FPS:', QLabel(str(stream.fps)))
        inner_layout.addRow('Format:', QLabel(str(stream.format)))
        self.vcodec_combo = VideoCombo()
        inner_layout.addRow('Codec:', self.vcodec_combo)
        conf_layout = QHBoxLayout()
        self.bitrate_edit = BitrateLineEdit('1.5M')
        conf_layout.addWidget(self.bitrate_edit)
        btnconf = QPushButton('Configure')
        conf_layout.addWidget(btnconf)        
        btnconf.clicked.connect(self.codec_dialog)
        inner_layout.addRow('Bitrate:', conf_layout)
        self.pass_spin = SpinBox(2)
        self.pass_spin.setRange(1, 2)
        inner_layout.addRow('Passes:', self.pass_spin)

        cslayout = QHBoxLayout()
        self.cropgroup = CodecGroup('Crop', 'crop', None, self, True)
        croplayout = QFormLayout()
        self.cropgroup.spnCropHoriz = SpinBox(0)
        croplayout.addRow('Horizontal:', self.cropgroup.spnCropHoriz )
        self.cropgroup.spnCropVertical = SpinBox(0)
        croplayout.addRow('Vertical:', self.cropgroup.spnCropVertical)
        self.cropgroup.spnCropWidth = SpinBox(stream.width)
        croplayout.addRow('Width:', self.cropgroup.spnCropWidth)
        self.cropgroup.spnCropHeight = SpinBox(stream.height)
        croplayout.addRow('Height:', self.cropgroup.spnCropHeight)
        self.cropgroup.btnCropDetect = detbutton = QPushButton('Detect')
        detbutton.clicked.connect(self.on_cropdetect_clicked)
        croplayout.addRow(detbutton)
        
        self.cropgroup.setLayout(croplayout)
        cslayout.addWidget(self.cropgroup)
        
        self.scalegroup = CodecGroup('Scale', 'scale', None, self, True)
        scalelayout = QFormLayout()
        self.scalegroup.spnWidth = SpinBox(stream.width)
        scalelayout.addRow('Width:', self.scalegroup.spnWidth)
        self.scalegroup.spnHeight = SpinBox(stream.height)
        scalelayout.addRow('Height:', self.scalegroup.spnHeight)
        self.scalegroup.chkLAR = QCheckBox('Lock Aspect Ratio')
        self.scalegroup.chkLAR.stateChanged.connect(self.scalegroup.spnHeight.setDisabled)
        self.scalegroup.chkLAR.setChecked(True)
        scalelayout.addRow(self.scalegroup.chkLAR)
        
        self.scalegroup.setLayout(scalelayout)
        cslayout.addWidget(self.scalegroup)
        
        inner_layout.addRow(cslayout)
        self.setLayout(inner_layout)

    def make_video_opts(self, stream_num):
        video_opts = Options()
        codec_opt = Options('-codec', stream_num, sep=':')
        video_opts.extend((codec_opt, _video_codecs[self.vcodec_combo.currentText()]))
        if self.vcodec_combo.currentText() != 'Copy':
            bitrate_opt = Options('-b', stream_num, sep=':')
            video_opts.append(Options(bitrate_opt, self.bitrate_edit.text()))
        if self.codec_extra is not None:
            for k, v in self.codec_extra.items():
                o = Options(k, stream_num, sep=':')
                p = Options(o, v)
                video_opts.append(p)
        children = self.findChildren(CodecGroup)
        filter = Options()
        filter_chain = Options(sep=',')
        filter.extend((Options('-filter', stream_num, sep=':'), filter_chain))
        if any([c.isChecked() for c in children]):
            for child in children:
                if child.isChecked():
                    if child.codec_type == 'crop':
                        crop_opt = Options('crop', sep='=')
                        crop_parms = Options('{}'.format(child.spnCropWidth.value()), 
                                                             '{}'.format(child.spnCropHeight.value()), 
                                                             '{}'.format(child.spnCropHoriz.value()), 
                                                             '{}'.format(child.spnCropVertical.value()),  sep=':')
                        crop_opt.append(crop_parms)
                        filter_chain.insert(0, crop_opt)
                    elif child.codec_type == 'scale':
                        scale_opt = Options('scale', sep='=')
                        scale_parms = Options('w={}'.format(child.spnWidth.value()), 
                                                              'h={}'.format(child.chkLAR.isChecked() and '-1' 
                                                              or child.spnHeight.value()), 
                                                              sep=':')
                        scale_opt.append(scale_parms)
                        filter_chain.append(scale_opt)
            filter_chain.append('hqdn3d')
            video_opts.append(filter)
            video_opts.extend((Options('-strict', stream_num, sep=':'), 'experimental'))
        return video_opts
        
    @pyqtSlot()
    def codec_dialog(self):
        if self.codec_type == 'video':
            if self.vcodec_combo.currentText() == 'H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10':
                window = H264Dialog(self, self.codec_extra)
                window.exec_()
                if window.returnval is not None:
                    self.codec_extra = window.returnval

    @pyqtSlot()
    def on_cropdetect_clicked(self):
        cropdetect = CropDetect(self.cropdata, self.stream)
        self.cropdata.connect(self.on_crop_data)
        self.cropgroup.btnCropDetect.setDisabled(True)
        cropdetect.start()
        
    @pyqtSlot(tuple)
    def on_crop_data(self, croplist):
        clist = [c for c in map(int, croplist)]
        if (clist[0] + clist[2]) <= self.stream.width:
            self.cropgroup.spnCropWidth.setValue(clist[0])
            self.cropgroup.spnCropHoriz.setValue(clist[2])
        if (clist[1] + clist[3]) <= self.stream.height:
            self.cropgroup.spnCropHeight.setValue(clist[1])
            self.cropgroup.spnCropVertical.setValue(clist[3])
        self.cropgroup.btnCropDetect.setEnabled(True)
        
class SubtitleCombo(QComboBox):
    codecs = {'Copy': 'copy', 
                      'DVD subtitles': 'dvdsub', 
                      'DVB subtitles': 'dvbsub', 
                      'XSUB': 'xsub', 
                      'SSA (SubStation Alpha)': 'ssa'
                    }
                    
    def __init__(self, parent=None):
        super().__init__(parent)
        codecs = list(self.codecs.keys())
        codecs.sort(key=str.lower)
        idx = codecs.index('Copy')
        codecs.insert(0, codecs.pop(idx))
        self.addItems(codecs)
        
class AudioCombo(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        codecs = list(_audio_codecs.keys())
        codecs.sort(key=str.lower)
        try:
            pref_index = codecs.index('MP3 (MPEG audio layer 3)')
        except ValueError:
            pref_index = 0
        self.addItems(codecs)
        self.setCurrentIndex(pref_index)
        
class BitrateLineEdit(QLineEdit):
    def __init__(self, contents='', parent=None):
        super().__init__(contents, parent)
        self.setValidator(BitrateValidator())

class VideoCombo(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        codecs = list(_video_codecs.keys())
        codecs.sort(key=str.lower)
        try:
            pref_index = codecs.index('H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10')
        except ValueError:
            pref_index = 0
        self.addItems(codecs)
        self.setCurrentIndex(pref_index)

class AverageDeque(deque):
    BUFLEN = 64
    
    def __init__(self):
        iterable = [0] * self.BUFLEN
        super().__init__(iterable, self.BUFLEN)
        self.total = sum(iterable)
        
    @property
    def average(self):
        return self.total / self.maxlen
        
    def pop(self):
        value = super().pop()
        self.total -= value
        return value
        
    def push(self, value):
        self.pop()
        self.total += value
        self.appendleft(value)

class QualityBar(QProgressBar):
    MAX = 310
    MID = 150
    
    def __init__(self, parent=None):
        super().__init__(parent)
        palette = QPalette(self.palette())
        palette.setColor(QPalette.Highlight, QColor(Qt.green))
        palette.setColor(QPalette.Window, QColor(Qt.red))
        self.setPalette(palette)
        self.setRange(0, self.MAX)
        self.setTextVisible(False)
        self.buffer = AverageDeque()
        
    def setValue(self, value):
        value = self.MAX if value > self.MAX else value
        value = 0 if value < 0 else value
        self.buffer.push(value)
        value = int(round(self.buffer.average))
        value = self.MAX - value                
        super().setValue(value)

class CropDetect(Thread):
    samples = 5
    
    def __init__(self, datasig, stream):
        super().__init__()
        self.datasig = datasig
        self.stream = stream
        
    def run(self):
        recrop = re.compile(
            r'\(-vf crop=(?P<width>\d+):(?P<height>\d+):(?P<horiz>\d+):(?P<vert>\d+)\)')
        widfreq = Counter(); hgtfreq = Counter(); horfreq = Counter(); verfreq = Counter()
        length = self.stream.length.total_seconds()        
        sample_points = (p*length/self.samples for p in range(1, self.samples))
        for point in sample_points:
            mplayer = Commands().make_command('mplayer')
            mplayer.add_options(
                'dvd://{}'.format(self.stream.ix), 
                '--dvd-device={}'.format(self.stream.device), 
                '--vo=null', 
                '--ss={}'.format(point), 
                '--frames=100', 
                '--nosound', 
                '--benchmark', 
                '--vf=cropdetect=round,format=yv12'
            )
            mplayer_proc = subp.Popen(
                mplayer.gen_command(), 
                stdout=subp.PIPE, 
                stderr=subp.DEVNULL, 
                universal_newlines=True)
            for mpop in mplayer_proc.stdout:
                match = recrop.search(mpop)
                if match:
                    widfreq[match.group('width')] += 1
                    hgtfreq[match.group('height')] += 1
                    horfreq[match.group('horiz')] += 1
                    verfreq[match.group('vert')] += 1
        try:
            self.datasig.emit((
                widfreq.most_common(1)[0][0], 
                hgtfreq.most_common(1)[0][0], 
                horfreq.most_common(1)[0][0], 
                verfreq.most_common(1)[0][0]))
        except:
            self.datasig.emit(['0'] * 4)

class SourceTreeView(QTreeView):
    def rowsInserted(self, index, start, end):
        super().rowsInserted(index, start, end)
        if index.isValid():
            node = index.internalPointer()
            if node.typeinfo == 'DVD_Drive':
                self.expand(index)
