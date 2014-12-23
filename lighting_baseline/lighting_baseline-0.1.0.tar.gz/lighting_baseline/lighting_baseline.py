#---------------------------------------------------------------------------------------
#Lighting Fault Detection and Energy Quantification (c)2014,
#The Regents of the University of California, through Lawrence Berkeley National
#Laboratory (subject to receipt of any required approvals from the U.S.
#Department of Energy).  All rights reserved.
#
#If you have questions about your rights to use or distribute this software,
#please contact Berkeley Lab's Technology Transfer Department at TTD@lbl.gov
#referring to "Lighting Fault Detection and Energy Quantification (LBNL Ref 2014-173)".
#
#NOTICE:  This software was produced by The Regents of the University of
#California under Contract No. DE-AC02-05CH11231 with the Department of Energy.
#For 5 years from November 25, 2014, the Government is granted for itself and
#others acting on its behalf a nonexclusive, paid-up, irrevocable worldwide
#license in this data to reproduce, prepare derivative works, and perform
#publicly and display publicly, by or on behalf of the Government. There is
#provision for the possible extension of the term of this license. Subsequent to
#that period or any extension granted, the Government is granted for itself and
#others acting on its behalf a nonexclusive, paid-up, irrevocable worldwide
#license in this data to reproduce, prepare derivative works, distribute copies
#to the public, perform publicly and display publicly, and to permit others to
#do so. The specific term of the license can be identified by inquiry made to
#Lawrence Berkeley National Laboratory or DOE. Neither the United States nor the
#United States Department of Energy, nor any of their employees, makes any
#warranty, express or implied, or assumes any legal liability or responsibility
#for the accuracy, completeness, or usefulness of any data, apparatus, product,
#or process disclosed, or represents that its use would not infringe privately
#owned rights.
#---------------------------------------------------------------------------------------

import csv
import utils
import tempfile
import logging

from os import path
from series import Series
from subprocess import Popen, PIPE

class Lighting_Analysis(object):
    
    def __init__(self, load_data, 
                 timezone=None, sq_ft=None,
                 log_level=logging.INFO):
        """load_data may be:
                - List of Tuples containing timestamps and values
                - filename of a csv containing timestamps and values
                - Series object
        """
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger(__name__)
        
        if timezone == None: self.logger.warn("Assuming timezone is OS default")
        
        self.timezone   = utils.get_timezone(timezone)
        self.model_dir  = path.join(path.dirname(path.abspath(__file__)), 'r')
        self.sq_ft      = sq_ft
        
        self.load_series  = self._get_series(load_data)
        
        self._stderr = None
        self._stdout = None
        
        self._reset_derivative_data()
        
    # ----- derivative data generators ----- #
    # summary:             generates summary statistics for the input data
    #
    def summary(self,
                 workdays='12345',workday_start='06:30',
                 verbosity='1'):
        import shutil
        from datetime import datetime
        """summary : compiles necessary temporary files and
        shells out to R script:
        - training power data: timestamps and kW
        
        LightingSummary.R
            --loadFile=LOAD_FILE
            --summaryStatisticsFile=SUMMARY_STATISTICS_FILE
            --workDays=WORKDAYS
            --workdayStart=WORKDAYSTART
        """
        self._reset_derivative_data()
          
        # ----- write temporary files ----- #
        power_tmp       = self.load_series.write_to_tempfile()        
        summary_stats_tmp = tempfile.NamedTemporaryFile()
        
        
        # ----- build command ----- #
        cmd = path.join(self.model_dir, 'LightingSummary.R')
        cmd += " --loadFile=%s"                 % power_tmp.name
        cmd += " --summaryStatisticsFile=%s"    % summary_stats_tmp.name
        cmd += " --workDays=%s"                 % workdays
        cmd += " --workdayStart=%s"             % workday_start
        cmd += " --verbosity=%s"                % verbosity
        
        # ----- run script ----- #
        self._run_script(cmd)
        
        # ----- process results ----- #
        self.stats = self._read_summary_stats(summary_stats_tmp.name)
        return self.stats

    def _run_script(self, command):
        self.logger.info("Running R script...")

        p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        self._stdout = stdout
        self._stderr = stderr

        if stderr:
            self.logger.error(" --- R script error: --- ")
            for l in stderr.splitlines(): print " --> %s" % l

        if stdout:
            self.logger.info(" --- R script info: --- ")
            for l in stdout.splitlines(): print " --> %s" % l

        return True        
         
    def add_exclusion(self, start_at, end_at):
        """proxy add_exclusion to series"""
        self.training_load_series.add_exclusion(start_at, end_at)
        
    def add_named_exclusion(self, exclusion_name):
        """proxy add_named_exclusion to series"""
        self.training_load_series.add_named_exclusion(exclusion_name)
        
    def clear_exclusions(self):
        """proxy clear_exclusion to series"""
        self.training_load_series.clear_exclusions()
        
    def _get_series(self, data):
        """returns a series built from the data arg
        - if the data arg is None: return None
        - if the data arg is a Series: return the Series
        - if the data arg is a string: attempt to build Series from file path
        - if the data arg is a List: attempt to build Series from list
        """
        if (isinstance(data, Series)) | (data == None):
            return data
        else:
            return Series(data, self.timezone)
 
            
    def _read_summary_stats(self, summary_stats_file):
        """read summary stats file and return values"""
        summary_stats = {}
        
        with open(summary_stats_file, 'r') as f:
            for ent in csv.reader(f):
                if ent: summary_stats[ent[0].lower()] = float(ent[1])            
        return summary_stats
        
    def _reset_derivative_data(self):
        self.summary_stats                    = None

class Lighting_Compare(object):
    def __init__(self, baseline_load_data,comparison_load_data, 
                 timezone=None, sq_ft=None,
                 log_level=logging.INFO):
        """load_data may be:
                - List of Tuples containing timestamps and values
                - filename of a csv containing timestamps and values
                - Series object
        """
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger(__name__)
        
        self.timezone   = timezone
        self.sq_ft = sq_ft

        
        self.baseline_load_data = baseline_load_data
        self.comparison_load_data = comparison_load_data
        
    def change(self, workdays='12345', workday_start='06:30', verbosity='1'):  
        """Find change in electric load in different time periods
        """
        
        l1 = Lighting_Analysis(self.baseline_load_data,timezone=self.timezone,sq_ft=self.sq_ft)
        l2 = Lighting_Analysis(self.comparison_load_data,timezone=self.timezone,sq_ft=self.sq_ft)
        
        s1 = l1.summary(workdays, workday_start, verbosity)
        s2 = l2.summary(workdays, workday_start, verbosity)
        
        change={}
        for k in s1.keys():
             change[k] = float(s2[k]) - float(s1[k])
        
        return change
       
        
           

