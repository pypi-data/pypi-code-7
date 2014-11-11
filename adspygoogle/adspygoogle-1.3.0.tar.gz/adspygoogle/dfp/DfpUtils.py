#!/usr/bin/python
#
# Copyright 2011 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Handy utility functions."""

__author__ = 'Nicholas Chen'

import csv
import datetime
import os
import time
import urllib2

from adspygoogle.common import SanityCheck
from adspygoogle.common import Utils
from adspygoogle.dfp import LIB_HOME
import pytz

# The suggested page limit per page fetched from the API.
PAGE_LIMIT = 500
# The chunk size used for report downloads.
_CHUNK_SIZE = 16 * 1024


class FilterStatement(object):
  """A statement object for PQL and get*ByStatement queries.

  The FilterStatement object allows for user control of limit/offset. It
  automatically limits queries to the suggested page limit if not explicitly
  set.
  """

  def __init__(
      self, where_clause='', values=None, limit=PAGE_LIMIT, offset=0):
    self.where_clause = where_clause
    self.values = values
    self.limit = limit
    self.offset = offset

  def _GetOffset(self):
    return self._offset

  def _SetOffset(self, value):
    self._offset = value

  offset = property(_GetOffset, _SetOffset)

  def _GetLimit(self):
    return self._limit

  def _SetLimit(self, value):
    self._limit = value

  limit = property(_GetLimit, _SetLimit)

  def IncreaseOffsetBy(self, increase_offset):
    self.offset += increase_offset

  def ToStatement(self):
    return {'query': '%s LIMIT %d OFFSET %d' %
                     (self.where_clause, self._limit, self._offset),
            'values': self.values}


def GetCurrencies():
  """Get a list of available currencies.

  Returns:
    list available currencies.
  """
  return Utils.GetDataFromCsvFile(
      os.path.join(LIB_HOME, 'data', 'currencies.csv'))


def GetTimezones():
  """Get a list of available timezones.

  Returns:
    list Available timezones.
  """
  return Utils.GetDataFromCsvFile(
      os.path.join(LIB_HOME, 'data', 'timezones.csv'))


def _PageThroughPqlSet(pql_service, pql_query, output_function, values):
  """Pages through a pql_query and performs an action (output_function).

  Args:
    pql_service: ApiService an instance of pqlService.
    pql_query: str a statement filter to apply (the query should not include
               the limit or the offset)
    output_function: the function to call to output the results (csv or in
                     memory)
    values: list dict of bind values to use with the pql_query.
  """
  offset, result_set_size = 0, 0

  while True:
    filter_statement = {
        'query': '%s LIMIT %s OFFSET %s' % (
            pql_query, PAGE_LIMIT, offset),
        'values': values
    }
    response = pql_service.select(filter_statement)[0]

    if 'rows' in response:
      # Write the header row only on first pull
      if offset == 0:
        header = response['columnTypes']
        output_function([label['labelName'].encode('utf-8')
                         for label in header])

      entities = response['rows']
      result_set_size = len(entities)

      for entity in entities:
        output_function([_ConvertValueForCsv(value) for value
                         in entity['values']])

      offset += result_set_size
      if result_set_size != PAGE_LIMIT:
        break
    elif offset == 0:
      break


def DownloadPqlResultToList(pql_service, pql_query, values=None):
  """Downloads the results of a PQL query to a list.

  Args:
    pql_service: ApiService an instance of pqlService.
    pql_query: str a statement filter to apply (the query should not include
               the limit or the offset)
    [optional]
    values: list dict of bind values to use with the pql_query.

  Returns:
    a list of lists with the first being the header row and each subsequent
    list being a row of results.
  """
  results = []
  _PageThroughPqlSet(pql_service, pql_query, results.append, values)

  return results


def DownloadPqlResultSetToCsv(
    pql_service, pql_query, file_handle, values=None):
  """Downloads the results of a PQL query to CSV.

  Args:
    pql_service: ApiService an instance of pqlService.
    pql_query: str a statement filter to apply (the query should not include
               the limit or the offset)
    file_handle: file the file object to write to.
    [optional]
    values: list dict of bind values to use with the pql_query.

  Returns:
    the file that the data was written to.
  """
  pql_writer = csv.writer(open(file_handle.name, 'wb'), delimiter=',',
                          quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
  _PageThroughPqlSet(pql_service, pql_query, pql_writer.writerow, values)

  return file_handle


def _ConvertValueForCsv(pql_value):
  """Sanitizes a field value from a Value object to a CSV suitable format.

  Args:
    pql_value: dict a dictionary containing the data for a single field of an
               entity.

  Returns:
    str a CSV writer friendly value formatted by Value_Type.
  """
  field = pql_value['value']

  if pql_value['Value_Type'] == 'TextValue':
    return field.encode('utf-8')
  elif pql_value['Value_Type'] == 'NumberValue':
    return float(field) if '.' in field else int(field)
  elif pql_value['Value_Type'] == 'DateTimeValue':
    return _ConvertDateTimeToOffset(field)
  elif pql_value['Value_Type'] == 'DateValue':
    return datetime.date(int(field['date']['year']),
                         int(field['date']['month']),
                         int(field['date']['day'])).isoformat()
  else:
    return field


def _ConvertDateTimeToOffset(date_time_value):
  """Converts the PQL formatted response for a dateTime object.

  Output conforms to ISO 8061 format, e.g. 'YYYY-MM-DDTHH:MM:SSz.'

  Args:
    date_time_value: dict The date time value from the PQL response.

  Returns:
    str A string representation of the date time value uniform to ReportService.
  """
  date_time_obj = datetime.datetime(int(date_time_value['date']['year']),
                                    int(date_time_value['date']['month']),
                                    int(date_time_value['date']['day']),
                                    int(date_time_value['hour']),
                                    int(date_time_value['minute']),
                                    int(date_time_value['second']))
  date_time_str = pytz.timezone(
      date_time_value['timeZoneID']).localize(date_time_obj).isoformat()

  if date_time_str[-5:] == '00:00':
    return date_time_str[:-6] + 'Z'
  else:
    return date_time_str


def DownloadReportToFile(report_job_id, export_format, service, outfile):
  """Download report data and write to a file.

  Args:
    report_job_id: str ID of the report job.
    export_format: str Export format for the report file.
    service: GenericDfpService A service pointing to the ReportService.
    outfile: file the file object to write to. If no file handle is passed in, a
          temporary file will be created.
  """
  SanityCheck.ValidateTypes(((report_job_id, (str, unicode)),))

  # Wait for report to complete.
  status = service.GetReportJob(report_job_id)[0]['reportJobStatus']
  while status != 'COMPLETED' and status != 'FAILED':
    if Utils.BoolTypeConvert(service._config['debug']):
      print 'Report job status: %s' % status
    time.sleep(30)
    status = service.GetReportJob(report_job_id)[0]['reportJobStatus']

  if status == 'FAILED':
    if Utils.BoolTypeConvert(service._config['debug']):
      print 'Report process failed'
    return ''
  else:
    if Utils.BoolTypeConvert(service._config['debug']):
      print 'Report has completed successfully'

  # Get report download URL.
  report_url = service.GetReportDownloadURL(report_job_id, export_format)[0]
  response = urllib2.urlopen(report_url)
  while True:
    chunk = response.read(_CHUNK_SIZE)
    if not chunk: break
    outfile.write(chunk)
