#!/home/cpro/.pyenv/versions/3.4.1/bin/python
#Simple nosetests xml report merge tool
import sys
import logging
import xml.dom.minidom

def inc_value(value,name,node):
    '''Increment global value with node attribute values'''
    ival = 0
    try:
       sval = node.attributes[name].value
       ival = int(sval)
    finally:
        return value + ival

if __name__ == "__main__":
  lg_format = '%(asctime)s : %(message)s'
  lg_dateformat = '%Y.%m.%d %H:%M:%S'
  logging.basicConfig(format=lg_format, datefmt=lg_dateformat)
  log = logging.getLogger('nosemerge')
  log.setLevel(10)
  if len(sys.argv)<3:
    log.error('Invalid parameters!\n  Usage example: nosetests.py input1.xml input2.xml inputN.xml output.xml')
    sys.exit(1)
  infiles = sys.argv[1:-1]
  outfile = sys.argv[-1]
  log.debug('Input files: {}'.format(str(infiles)))
  log.debug('Output file: {}'.format(outfile))

  out_xml = xml.dom.minidom.Document()
  root = out_xml.createElement('testsuite')
  out_xml.appendChild(root)

  tests=0
  errors=0
  failures=0
  skip=0

  for file in infiles:
    log.debug('Parsing {}'.format(file))
    in_xml = xml.dom.minidom.parse(file)

    with in_xml.getElementsByTagName('testsuite')[0] as testsuite:
      tests = inc_value(tests,'tests',testsuite)
      errors = inc_value(errors,'errors',testsuite)
      failures = inc_value(failures,'failures',testsuite)
      skip = inc_value(skip,'skip',testsuite)
      log.debug('Aggregated values: tests {}, errors {}, failures {}, skip {}'.format(
                  tests,errors,failures,skip))
      for case in testsuite.getElementsByTagName('testcase'):
        root.appendChild(case)
    in_xml.unlink()

  root.setAttribute('name','nosetests')
  root.setAttribute('tests',str(tests))
  root.setAttribute('errors',str(errors))
  root.setAttribute('failures',str(failures))
  root.setAttribute('skip',str(skip))
  log.debug('Writing output XML')
  with open(outfile,'w') as fd:
    out_xml.writexml(fd,encoding='UTF-8')
  out_xml.unlink()
  log.debug('Done!')
