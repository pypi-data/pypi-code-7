# -*- coding: utf-8 -*-
'''
Created on Nov 25, 2014

Simple GUI

@author: Arturo Curiel
'''

import sys
import os
import cv2.cv as cv

from PyQt4 import Qt, QtCore, QtGui

from nixtla.core.tools import default_config_ini
from nixtla.core.tools import default_database_ini
from nixtla.core.tools import default_rules_ini

import ConfigParser


class TextEditDialog(Qt.QDialog):

    def __init__(self, path, defaults=None, parent = None):
        super(TextEditDialog, self).__init__(parent)

        layout = Qt.QVBoxLayout(self)
        self.isAccepted = None

        self.defaults = defaults
        self.text_edit = Qt.QTextEdit(self)
        
        with open(path, 'r') as f:
            self.text_edit.setText(f.read())
        
        self.init_text = self.text_edit.toPlainText()
        
        layout.addWidget(self.text_edit)

        # Save and Cancel buttons
        self.buttons = Qt.QDialogButtonBox(
                                        Qt.QDialogButtonBox.RestoreDefaults |\
                                        Qt.QDialogButtonBox.Save |\
                                        Qt.QDialogButtonBox.Cancel,
                                        Qt.Qt.Horizontal, self)
        layout.addWidget(self.buttons)
        
        self.buttons.button(Qt.QDialogButtonBox.RestoreDefaults).\
                                        clicked.connect(self.confirm_restore)
        self.buttons.accepted.connect(self.confirm_accept)
        self.buttons.rejected.connect(self.reject)
        
        self.setWindowTitle(os.path.basename(path))
    
    def confirmed(self, message):
        reply = QtGui.QMessageBox.question(self, 
                                           'Message',
                                           message, 
                                           QtGui.QMessageBox.Yes | 
                                           QtGui.QMessageBox.No,
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            return True
        else:
            return False
    
    def confirm_accept(self):
        if self.init_text == self.text_edit.toPlainText():
            return self.reject()
        if self.confirmed("Are you sure to override this configuration file?"):
            return self.accept()
    
    def confirm_restore(self, message):
        if self.confirmed("Are you sure you want to restore default values?"):
            self.restore()
        
    def restore(self):
        self.text_edit.setText(self.defaults)
            
    def accept(self):
        self.isAccepted = True
        return super(TextEditDialog, self).accept()
    
    def reject(self):
        self.isAccepted = False
        return super(TextEditDialog, self).reject()
    
            
class StartQT(Qt.QApplication):
    
    def __init__(self, args):
        """Simple interface to tweak config.ini before start"""

        Qt.QApplication.__init__(self, args)
        self.process = None
        
        initial_cursor_position = Qt.QCursor.pos()
        #resolution = QtGui.QDesktopWidget().screenGeometry(2)
        self.main_window = Qt.QWidget()
        self.main_window.setGeometry(initial_cursor_position.x()-320,
                                     initial_cursor_position.y()-240, 
                                     640, 
                                     480)
        
        self.config = ConfigParser.SafeConfigParser(allow_no_value=True)
        self.config.optionxform = str
        self.config.read("%s/res/config.ini" % sys.path[0])

        self.rulesfile = ConfigParser.SafeConfigParser(allow_no_value=True)
        self.rulesfile.optionxform = str
        self.rulesfile.read("%s/res/rules.ini" % sys.path[0])
        
        self.main_window.setWindowTitle("Nixtla formulae based annotator")
        
        self.main_layout = Qt.QVBoxLayout()
        self.main_layout.addStretch(1)
        
        self.create_status_viewer()
        self.create_main_form()
        self.create_waiting_message()
        self.create_buttons()
        
        self.main_window.setLayout(self.main_layout)
        self.main_window.show()
        self.waiting_message.hide()
        sys.exit(self.exec_())
    
    def qimage_from_video(self, frame):
        # Load the file into a QMovie
        capture = cv.CreateFileCapture(self.config.get("Pipeline",
                                                       "annotation_video_path")
                                       )
        if capture == None:
            raise IOError("Couldn't open capture file")
         
        cv.SetCaptureProperty(capture,
                              cv.CV_CAP_PROP_POS_FRAMES,
                              frame)
        image = cv.QueryFrame(capture)
        cv.CvtColor(image, image, cv.CV_BGR2RGB)
        w, h = cv.GetSize(image)
        qtimage = Qt.QImage(image.tostring(), w, h, QtGui.QImage.Format_RGB888)
        del(capture)
        return qtimage

    def update_video_thumbnail(self):
        qtimage = self.qimage_from_video(200)
        pix = QtGui.QPixmap.fromImage(qtimage)
        pix = pix.scaled(370, 290, QtCore.Qt.KeepAspectRatio)
        self.status_info.setFixedWidth(630 - pix.size().width())
        self.qtimage_screen.setPixmap(pix)
        
    def update_status_info(self):
        data = "\n"
        data += " Loaded Posture rules:"
        for option in self.rulesfile.options("Posture"):
            data += "\n    %s" % option
        
        data += "\n\n"
        data += " Loaded Transition rules: "
        for option in self.rulesfile.options("Transition"):
            data += "\n    %s" % option

        data += "\n\n"
        data += "Tracker implementation: \n    %s" % self.config.get(
                                                            "TrackingModule", 
                                                            "implementedBy")
        self.status_info.setText(data)
            
    def create_status_viewer(self):
        status_container = QtGui.QSplitter(QtCore.Qt.Horizontal)

        self.qtimage_screen = Qt.QLabel()
        self.qtimage_screen.setAlignment(QtCore.Qt.AlignCenter)
        status_container.addWidget(self.qtimage_screen)
        
        self.status_info = QtGui.QLabel()
        self.status_info.setFrameStyle(QtGui.QFrame.StyledPanel)
        self.status_info.setMinimumWidth(240)
        self.status_info.setAlignment(QtCore.Qt.AlignLeft)
        self.status_info.setWordWrap(True)
        self.status_info.setIndent(True)
        status_container.addWidget(self.status_info)
        
        self.update_video_thumbnail()
        self.update_status_info()
        self.main_layout.addWidget(status_container)
            
    def create_main_form(self):
        grid = Qt.QGridLayout()
        grid.setSpacing(10)

        lab = Qt.QLabel
        self.video_text_line = self.standard_textline()
        self.tracker_text_line = self.standard_textline()
        self.results_text_line = self.standard_textline()
        
        v_butt = self.create_loadfile_button(self.update_video_path)
        t_butt = self.create_loadfile_button(self.update_tracker_path)
        r_butt = self.create_loadfile_button(self.update_eaf_path)
        
        form = [''                          , ''                    , ''    ,
                lab('Video:')               , self.video_text_line  , v_butt,
                lab('Tracker Results:')     , self.tracker_text_line, t_butt,
                ''                          , ''                    , ''    ,
                lab('Annotation save path:'), self.results_text_line, r_butt]
        
        self.update_form()
        positions = [(i, j) for i in range(5) for j in range(3)]
        
        for position, widget in zip(positions, form):
            if widget == '':
                continue
            grid.addWidget(widget, *position)
        self.main_layout.addLayout(grid)
    
    def update_form(self):
        
        video_path = self.config.get("Pipeline", "annotation_video_path")
        self.video_text_line.setText(video_path)
        
        tracker_path = self.config.get("TrackingModule", "tracking_files")
        tracker_path = tracker_path.replace("[", "")\
                                   .replace("]", "")\
                                   .replace(" ","")
        self.tracker_text_line.setText(tracker_path)
        
        results_path = self.config.get("Pipeline", "results_file_path")
        self.results_text_line.setText(results_path)
    
    def update(self):
        self.update_video_thumbnail()
        self.update_form()
        self.update_status_info()
    
    def standard_textline(self, default_txt=''):
        line = Qt.QLineEdit()
        line.setText(default_txt)
        line.setReadOnly(True)
        return line
    
    def create_loadfile_button(self, callback):
        but = Qt.QPushButton("Change")
        
        self.connect(but,
                     Qt.SIGNAL("clicked()"),
                     callback
                     )
        return but
    
    def change_config(self, section, option, results=None):
        if results:
            self.config.set(section, option, str(results))
            self.config.write(open("%s/res/config.ini" % sys.path[0], "w"))
            self.update()
    
    def update_video_path(self):
        result = QtGui.QFileDialog.getOpenFileName(self.main_window,
                                                   'Select file', 
                                                   '%s/res' % sys.path[0],
                                                   'Video Files (*.mp4 *.mpg *.mpeg *.avi *.mov)')
        result = str(result)
        if result != '':
            self.change_config("Pipeline", 
                               "annotation_video_path",
                                self.confirm("Are you sure you want to override"+\
                                            "this value?", result)
                               )
        
    def update_eaf_path(self):
        result = QtGui.QFileDialog.getSaveFileName(self.main_window,
                                                   'Select file', 
                                                   '%s/res' % sys.path[0],
                                                   '*.eaf')
        result = str(result)
        if result != '':
            if not result.endswith(".eaf"):
                result += ".eaf"
            self.change_config("Pipeline", 
                               "results_file_path", 
                               result
                               )
    
    def update_tracker_path(self):
        result = QtGui.QFileDialog.getOpenFileNames(self.main_window,
                                                   'Select file', 
                                                   '%s/res' % sys.path[0],
                                                   '*.txt')
        if len(result) != 0 and len(result) <= 2: # At most two signers
            if len(result) == 1:
                result = str(result[0])
            else:
                result = ", ".join(str(f) for f in result)
            
            self.change_config("TrackingModule", 
                               "tracking_files", 
                               self.confirm("Are you sure you want to override"+\
                                            "this value?", "[" + result + "]")
                               )
    
    def confirm(self, message, exit_value):
        reply = QtGui.QMessageBox.question(self.main_window, 
                                           'Message',
                                           message, 
                                           QtGui.QMessageBox.Yes | 
                                           QtGui.QMessageBox.No,
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            return exit_value
        else:
            return None
    
    def create_buttons(self):
        self.button_box = Qt.QHBoxLayout()
        self.button_box.addStretch(1)
        
        self.process_button = Qt.QPushButton("Generate Annotation")
        self.connect(self.process_button,
                     Qt.SIGNAL("clicked()"),
                     self.start_processing)
        self.button_box.addWidget(self.process_button)
        
        self.button_box.addSpacerItem(Qt.QSpacerItem(20,
                                                     40,
                                                     QtGui.QSizePolicy.Minimum,
                                                     QtGui.QSizePolicy.Expanding
                                                     )
                                      )
        
        self.config_ini_button = Qt.QPushButton("Modify config.ini")
        self.connect(self.config_ini_button,
                     Qt.SIGNAL("clicked()"),
                     self.open_config_ini)
        self.button_box.addWidget(self.config_ini_button)
        
        self.rules_ini_button = Qt.QPushButton("Modify rules.ini")
        self.connect(self.rules_ini_button,
                     Qt.SIGNAL("clicked()"),
                     self.open_rules_ini)
        self.button_box.addWidget(self.rules_ini_button)
        
        self.database_ini_button = Qt.QPushButton("Modify database.ini")
        self.connect(self.database_ini_button,
                     Qt.SIGNAL("clicked()"),
                     self.open_database_ini)
        self.button_box.addWidget(self.database_ini_button)
        
        self.button_box.addSpacerItem(Qt.QSpacerItem(20,
                                                     40,
                                                     QtGui.QSizePolicy.Minimum,
                                                     QtGui.QSizePolicy.Expanding
                                                     )
                                      )
        
        self.quit_button = Qt.QPushButton("Quit")
        self.connect(self.quit_button, 
                     Qt.SIGNAL("clicked()"),
                     self.quit)
        self.button_box.addWidget(self.quit_button)
        self.main_layout.addLayout(self.button_box)
    
    def create_waiting_message(self):
        waiting_message_layout = Qt.QHBoxLayout()
        waiting_message_label = Qt.QLabel("Generating annotation...")
        waiting_message_label.setAlignment(QtCore.Qt.AlignCenter)
        waiting_message_layout.addWidget(waiting_message_label)
        
        self.waiting_message = Qt.QWidget()
        self.waiting_message.setWindowTitle("Please wait...")
        self.waiting_message.setLayout(waiting_message_layout)
    
    def open_config_ini(self):
        self.edit_file("%s/res/config.ini" % sys.path[0], 
                       default_config_ini)
        self.config.read("%s/res/config.ini" % sys.path[0])
        self.update()
                
    def open_rules_ini(self):
        self.edit_file("%s/res/rules.ini" % sys.path[0], 
                       default_rules_ini)
        
    def open_database_ini(self):
        self.edit_file("%s/res/database.ini" % sys.path[0], 
                       default_database_ini)

    def edit_file(self, file_path, default_values):
        file_to_edit = TextEditDialog(file_path, default_values)
        file_to_edit.setGeometry(self.main_window.pos().x()+100,
                                    self.main_window.pos().y()+100,
                                    640,
                                    480)
        if file_to_edit.exec_() :
            if file_to_edit.isAccepted:
                self.save_to_file(file_path,
                                  file_to_edit.text_edit.toPlainText())
                return True
        return False
    
    def save_to_file(self, file_path, new_text):
        with open(file_path, "w") as f:
            f.write(new_text)
        
    def show_message(self):
        new_geometry = (self.main_window.pos().x() +\
                self.main_window.size().width()/2 - 150,
                self.main_window.pos().y() +\
                self.main_window.size().height()/2 - 50,
                300,
                100
                )
        self.main_window.setVisible(False)
        self.waiting_message.setGeometry(*new_geometry)
        self.waiting_message.show()
        
    def end_processing(self):
        new_geometry = (self.waiting_message.pos().x() -\
                self.main_window.size().width()/2 + 150,
                self.waiting_message.pos().y() -\
                self.main_window.size().height()/2 + 50,
                640,
                480
                )
        self.waiting_message.hide()
        self.main_window.setGeometry(*new_geometry)
        self.main_window.setVisible(True)
        QtGui.QMessageBox.about(self.main_window, 
                               'Message',
                               "Annotation created!")
        
    def start_processing(self):
        self.show_message()
        self.process = QtCore.QProcess(self)
        self.process.finished.connect(self.end_processing)
        self.process.start(sys.executable, [os.getcwd()+"/start.py"])
        