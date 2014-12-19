# -*- coding: utf-8 -*-

"""
Module implementing BR_MainWindow.
"""

from PyQt4.QtGui import (QMainWindow, QFileDialog, QMessageBox, QLabel, QVBoxLayout, 
    QRadioButton, QWidget)
from PyQt4.QtCore import pyqtSlot, QModelIndex, pyqtSignal
from .Ui_br_mainwindow import Ui_BR_MainWindow
from .br_jobdock import BR_JobDock
from baserip.dvd import DVDTreeModel
from baserip.command import Commands, CommandError, Options
from baserip.encoders import Avconv
from baserip.forms import (SubtitleGroup, CodecGroup, AudioGroup, VideoGroup)
from baserip.utils import TrackSource
from baserip import _version
from io import StringIO
import subprocess as subp
import re
import os

class BR_MainWindow(QMainWindow, Ui_BR_MainWindow):
    """
    baserip main window.
    """
    encodeclose = pyqtSignal(str)
            
    def __init__(self, parent=None):
        
        super().__init__(parent)
        self.setupUi(self)
        
        try:
            self.cmds = Commands('lsdvd','mplayer','avconv')
        except CommandError as err:
            errmsg = """The following commands are not available (Baserip will not work properly)\n{}""".format('\n'.join(c for c in err.command))
            msg = QMessageBox(QMessageBox.Warning, 'Unmet Dependencies', errmsg)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            msg.exec_()
        else:
            self.cmds.register_command_class('avconv', Avconv)
        
        self.populate_dvd_tree()

        self.btnExit.clicked.connect(self.close)

        self.dvdtreemodel.rowsInserted.connect(self.on_rows_inserted)
        self.DVDTree.expanded.connect(self.on_dvdtree_expanded)
        self.DVDTree.currentChanged = self.on_dvd_sel_changed
        self.DVDTree.rowsAboutToBeRemoved = self.rowsAboutToBeRemoved
        
        self.tabWidget.currentChanged.connect(self.on_tab_changed)
        self.btnSelDir.clicked.connect(self.on_seldir_clicked)
        self.btnStart.clicked.connect(self.on_start_clicked)

        self.enable_tabs(False)
        
        self.jobs = {}
        self.formats = {}
        
        sblabel = QLabel('Baserip version: {}, \u00A9 2014, Geoff Clements'.format(_version))
        self.statusbar.addWidget(sblabel)

    def populate_dvd_tree(self):
        self.dvdtreemodel = DVDTreeModel(self)
        self.DVDTree.setModel(self.dvdtreemodel)
        self.DVDTree.resizeColumnToContents(0)
            
    def enable_tabs(self, enable):
        for tab in range(1, self.tabWidget.count()):
            self.tabWidget.setTabEnabled(tab, enable)
        if not enable:
            self.tabWidget.setCurrentIndex(0)
        
    def populate_formats(self):
        avconv = Commands().make_command('avconv', '-formats')
        formats = subp.check_output(avconv.gen_command(), stderr = subp.DEVNULL, 
            universal_newlines=True)
        refmt = re.compile(r'^\W+[^.]D?E{1}\W+(?P<ext>\w+)\W+(?P<desc>\w.*$)')
        with StringIO(formats) as formats:
            for format in formats:
                match = refmt.search(format)
                if match:
                    self.formats[match.group('desc')] = match.group('ext')
        widget = QWidget()
        layout = QVBoxLayout()
        flist = list(self.formats.keys())
        flist.sort(key=str.lower)
        for fmt in flist:
            radio = QRadioButton(fmt)
            layout.addWidget(radio)
        widget.setLayout(layout)
        self.FscrollArea.setWidget(widget)
        
    def populate_subtitles(self):
        widget = QWidget()
        layout = QVBoxLayout()
        for subt in self.source.subtitle_streams:
            groupbox = SubtitleGroup('Subtitle Stream {}'.format(subt.index), subt, self.SscrollArea)
            layout.addWidget(groupbox)
        widget.setLayout(layout)
        self.SscrollArea.setWidget(widget)
        
    def populate_audio(self):
        widget = QWidget()
        layout = QVBoxLayout()
        for audio in self.source.audio_streams:
            groupbox = AudioGroup('Audio Stream {}'.format(audio.index), audio, self.AscrollArea, 
                audio.index == 1)
            layout.addWidget(groupbox)
        widget.setLayout(layout)
        self.AscrollArea.setWidget(widget)
        
    def populate_video(self):
        widget = QWidget()
        layout = QVBoxLayout()
        vcount = 0
        for video in self.source.video_streams:
            groupbox = VideoGroup('Video Stream for Title {}'.format(video.index), 
                video, self.VscrollArea, vcount == 0)
            layout.addWidget(groupbox)        
            vcount += 1
        widget.setLayout(layout)
        self.VscrollArea.setWidget(widget)

        if not self.op_dir_edit.text():
            self.op_dir_edit.setText(os.path.join(os.environ['HOME'], '%T', 'Title_%N'))
        if not self.op_file_edit.text():
            self.op_file_edit.setText('%T_Title_%N')

        
    def gen_codec_groups(self):
        group_parents = (self.VscrollArea, self.AscrollArea, self.SscrollArea)
        for parent in group_parents:
            groups = parent.findChildren(CodecGroup)
            for group in groups:
                yield group
                
    @pyqtSlot(int)
    def on_tab_changed(self, page):
        if page == 4:
            if not self.formats:
                self.populate_formats()
                
    @pyqtSlot()
    def on_rows_inserted(self):
        self.DVDTree.resizeColumnToContents(0)
        
    @pyqtSlot(QModelIndex)
    def on_dvdtree_expanded(self, index):
        self.DVDTree.resizeColumnToContents(0)
    
    def make_source(self, node):
        if node.typeinfo == 'Track':
            return TrackSource(node)
        else:
            raise NotImplementedError
            
    def on_dvd_sel_changed(self, curr, prev):
        if not curr.isValid():
            self.textTrackInfo.clear()
            return

        node = curr.internalPointer()
        if node.typeinfo != 'Track':
            self.textTrackInfo.clear()
            self.enable_tabs(False)

        elif node.typeinfo == 'Track':
            self.DVDTree.resizeColumnToContents(1)
            self.textTrackInfo.clear()
            self.source = self.make_source(node)

            alist = self.source.audio_streams
            if alist:
                self.textTrackInfo.append('<b>Audio:</b>')
                for a in alist:
                    self.textTrackInfo.append(
                    '{0}: Language: <i>{1}</i>, Format: <i>{2}</i>, Channels: <i>{3}</i>'.format(
                        a.index, a.language, a.format, a.channels))
                self.textTrackInfo.append('<p></p>')

            slist = self.source.subtitle_streams
            if slist:
                self.textTrackInfo.append('<b>Subtitles:</b>')
                for s in slist:
                    self.textTrackInfo.append(
                        '{0}: Language: <i>{1}</i>'.format(s.index, s.language))
                        
            tuple(map(lambda obj: obj.deleteLater(), self.gen_codec_groups()))
            self.populate_subtitles()
            self.populate_audio()
            self.populate_video()
            self.enable_tabs(True)
        
    def rowsAboutToBeRemoved(self, parent, start, end):
        sel_list = self.DVDTree.selectedIndexes()
        if sel_list:
            pos = sel_list[0].parent().row()
            if pos is not None:
                if start <= pos <= end:
                    self.textTrackInfo.clear()
                    self.enable_tabs(False)
        
    @pyqtSlot()
    def on_seldir_clicked(self):
        dir = QFileDialog.getExistingDirectory(self, 'Select Output Directory',
            self.op_dir_edit.text(), 
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
            
        if dir:
            self.op_dir_edit.setText(dir)
            
    @pyqtSlot()
    def on_start_clicked(self):
        def mangle_name(name):
            name = re.sub('%T', self.source.title, name)
            name = re.sub('%N', str(self.source.track_number), name)
            name = re.sub('%L', str(self.source.length), name)
            name = re.sub('%f', self.source.title[0], name)
            return name
            
        job_id = self.source.unique_id
        if job_id in self.jobs:
            return
            
        avconv = Commands().make_command('avconv')
        avconv.global_opts.append('-y')
        avconv.infile_opts.append(Options('-fflags', '+genpts', '-i', 'pipe:0'))
        vcount = acount = scount = 0
        stream_id = 0
        passes = 1
        codec_groups = self.gen_codec_groups()
        for codec_group in codec_groups:
            if codec_group.isChecked():
                if codec_group.codec_type == 'video':
                    avconv.video_opts.append(codec_group.make_video_opts(stream_id))
                    passes = max(passes, codec_group.pass_spin.value())
                    vcount += 1
                elif codec_group.codec_type == 'audio':
                    avconv.audio_opts.append(codec_group.make_audio_opts(stream_id))
                    acount += 1
                elif codec_group.codec_type == 'subtitle':
                    avconv.subt_opts.append(codec_group.make_subt_opts(stream_id))
                    scount += 1
                if codec_group.codec_type in ('video', 'audio', 'subtitle'):
                    avconv.map_opts.append(codec_group.make_map_opt())
                    stream_id += 1
        if vcount == 0: avconv.map_opts.append('-vn')
        if acount == 0: avconv.map_opts.append('-an')
        if scount == 0:
            avconv.map_opts.append('-sn')
        else:
            avconv.infile_opts.insert(0, 
                Options('-analyzeduration', '200M', '-probesize', '400M'))

        fbuttons = self.FscrollArea.findChildren(QRadioButton)
        for button in fbuttons:
            if button.isChecked():
                format = self.formats[button.text()]
                avconv.format_opts.append(Options('-f', format))
                break
        
        opdir = self.op_dir_edit.text() or os.path.join(os.environ['HOME'], '%T', 'Title_%N')
        opdir = mangle_name(opdir)
        if not os.path.isdir(opdir):
            try:
                os.makedirs(opdir)
            except:
                return
        fname = self.op_file_edit.text() or '%T_Title_%N'
        fname = mangle_name(fname)
        avconv.outfile = os.path.join(opdir, fname)
        
        jobwin = BR_JobDock(avconv, passes, job_id, self.encodeclose, self.source, self)
        self.jobs[job_id] = jobwin
        jobwin.show()
        jobwin.start(opdir)
             
    @pyqtSlot(str)
    def on_jobclose(self, job_id):
        try:
            del self.jobs[job_id]
        except:
            pass
            
    def closeEvent(self, event):
        if self.jobs:
            msg = QMessageBox(
                QMessageBox.Question, 
                'Exiting Baserip', 
                'There are running jobs!\nAre you sure you want to exit Baserip?')
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            ans = msg.exec_()
            if ans == QMessageBox.Yes:
                for job in self.jobs:
                    self.jobs[job].cancel()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
            
