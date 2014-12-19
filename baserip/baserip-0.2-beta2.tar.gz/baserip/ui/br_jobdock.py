from PyQt4.QtCore import pyqtSlot, Qt, pyqtSignal
from PyQt4.QtGui import (QDockWidget, QMessageBox, QFormLayout, QLabel, QWidget, 
    QVBoxLayout, QHBoxLayout, QProgressBar, QPushButton, QIcon, QPixmap, QPlainTextEdit, QSizeGrip)
from threading import Thread, Event
from baserip.dvd import DvdTimeDelta
from baserip.forms import QualityBar
import subprocess as subp
import re
import copy

class BR_JobDock(QDockWidget):
    transcode_data = pyqtSignal([dict], [str]) 
    job_complete = pyqtSignal()

    def __init__(self, job, passes, job_id, closesig, source, parent=None):
        name = source.title
        super().__init__(name, parent)
        self.job = job
        self.passes = passes
        self.job_id = job_id
        self.closesig = closesig
        self.source = source

        self.setWindowTitle(name)
        self.setFeatures(QDockWidget.DockWidgetMovable|QDockWidget.DockWidgetFloatable)
        self.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.setFloating(True)

        self.widget = QWidget()
        layout = QVBoxLayout()
#        layout.setSizeConstraint(QVBoxLayout.SetFixedSize)
        message_layout = QFormLayout()
        self.lblPass = QLabel('Pass ? of {}'.format(passes))
        message_layout.addRow(self.lblPass)
        self.lblFrame = QLabel('?')
        message_layout.addRow('Frame:', self.lblFrame)
        self.lblFps = QLabel('?')
        message_layout.addRow('Frames per Second:', self.lblFps)
        self.lblSize = QLabel('?')
        message_layout.addRow('File Size:', self.lblSize)
        self.lblTime = QLabel('?')
        message_layout.addRow('Video Time:', self.lblTime)
        self.lblBitrate = QLabel('?')
        message_layout.addRow('Bitrate:', self.lblBitrate)
        layout.addLayout(message_layout)
        
        self.progressbar = QProgressBar()
        self.progressbar.setRange(0, self.source.length.total_seconds())
        layout.addWidget(self.progressbar)
        
        self.qualitybar = QualityBar()
        layout.addWidget(self.qualitybar)
        
        btn_layout = QHBoxLayout()
        btn_More = QPushButton('More')
        btn_More.setCheckable(True)
        btn_layout.addWidget(btn_More)
        btn_layout.addStretch()
        self.btnCancel = QPushButton('Close')
        self.btnCancel.setIcon(QIcon(QPixmap(':/icons/application-exit.png')))
        self.btnCancel.clicked.connect(self.on_cancel_clicked)
        btn_layout.addWidget(self.btnCancel)
        layout.addLayout(btn_layout)
        
        self.terminal = QPlainTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setShown(False)
#        self.terminal.setMinimumWidth(400)
        btn_More.toggled.connect(self.terminal.setVisible)
        layout.addWidget(self.terminal)
        
        griplayout = QHBoxLayout()
        griplayout.addWidget(QSizeGrip(self.widget))
        griplayout.addStretch()
        griplayout.addWidget(QSizeGrip(self.widget))
        layout.addLayout(griplayout)

        self.widget.setLayout(layout)
        self.setWidget(self.widget)
        
        self.transcode_data[dict].connect(self.on_avconv_data)
        self.transcode_data[str].connect(self.on_terminal_data)
        self.closesig.connect(parent.on_jobclose)
        
    def start(self, dir):
        self.runjob = TranscodeJob(self.job, self.passes, self.source, dir, self.transcode_data, 
            self.job_complete)
        self.runjob.completesig.connect(self.on_job_complete)
        self.btnCancel.setText('Stop')
        self.runjob.start()
      
    @pyqtSlot(dict)
    def on_avconv_data(self, match):
        self.lblPass.setText('Pass {pass} of {passes}'.format(**match))
        self.lblFrame.setText('{frame}'.format(**match))
        self.lblFps.setText('{fps}'.format(**match))
        size = round(int(match['size']) / 1024, 2)
        self.lblSize.setText('{} MB'.format(size))
        time = DvdTimeDelta(seconds=float(match['time']))
        self.lblTime.setText('{}'.format(time))
        self.lblBitrate.setText('{bitrate} kbps'.format(**match))
        self.qualitybar.setValue(int(round(float(match['q']) * 10)))
        self.progressbar.setValue(int(round(float(match['time']))))
        
    @pyqtSlot(str)
    def on_terminal_data(self, text):
        self.terminal.appendPlainText(text)
    
    @pyqtSlot()
    def on_cancel_clicked(self):
        if self.runjob.is_alive():
            msg = QMessageBox(QMessageBox.Question, 'Cancelling Job', 
                'Do you want to cancel the running job?')
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            ans = msg.exec_()
            if ans == QMessageBox.Yes:
                self.runjob.cancel()
        else:
            self.close_demand()
        
    @pyqtSlot()
    def on_job_complete(self):
        self.lblPass.setText('Completed')
        self.btnCancel.setText('Close')
        
    def close_demand(self):
        self.closesig.emit(self.job_id)
        self.close()
        
    def cancel(self):
        self.runjob.cancel()
        self.runjob.join()
    
class TranscodeJob(Thread):
    def __init__(self, job, passes, source, dir, datasig, completesig):
        super().__init__()
        self.job = job
        self.passes = passes
        self.dir = dir
        self.source = source
        self.datasig = datasig
        self.completesig = completesig
        self._cancel = Event()
        
    def run(self):
        self.remop = re.compile(
            r'^frame=\W*(?P<frame>\d+)\W+fps=\W*(?P<fps>\d+)\W+q=\W*(?P<q>\d+\.\d+)\W+size=\W*(?P<size>\d+)kB\W+time=\W*(?P<time>\d+\.\d+)\W+bitrate=\W*(?P<bitrate>\d+\.\d+)kbits/s')
        self.remop2 = re.compile(
            r'^size=\W*(?P<size>\d+)kB\W+time=\W*(?P<time>\d+\.\d+)\W+bitrate=\W*(?P<bitrate>\d+\.\d+)kbits/s')
        try:
            for jobpass in range(1, self.passes + 1):
                curjob = copy.deepcopy(self.job)
                if self.passes > 1:
                    curjob.video_opts.append('-pass {}'.format(jobpass))
#                    if jobpass == 1:
#                        curjob.outfile_opts[0] = Options('/dev/null')
                source = self.source.stream_data
                proc = subp.Popen(curjob.gen_command(), stdin=source.stdout, stdout=subp.DEVNULL, 
                    stderr=subp.PIPE, cwd=self.dir, universal_newlines=True)
                    
                for avcop in proc.stderr:
                    if self._cancel.is_set():
                        source.terminate()
                        proc.communicate()
                        source.communicate()
                        source.wait()
                        proc.terminate()
                        proc.wait()
                        return
                    match = self.remop.search(avcop)
                    if match:
                        avc_data = match.groupdict()
                        avc_data['pass'] = jobpass
                        avc_data['passes'] = self.passes
                        self.datasig[dict].emit(avc_data)
                    else:
                        match = self.remop2.search(avcop)
                        if match:
                            avc_data = match.groupdict()
                            avc_data['pass'] = jobpass
                            avc_data['passes'] = self.passes
                            avc_data['frame'] = '0'
                            avc_data['fps'] = '0'
                            avc_data['q'] = '0'
                            self.datasig[dict].emit(avc_data)
                        else:
                            self.datasig[str].emit(avcop)
                        
        except subp.SubprocessError:
            return
            
        finally:
            self.completesig.emit()
                        
    def cancel(self):
        self._cancel.set()
