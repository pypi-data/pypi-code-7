__author__ = 'Steven LI'

import pytest
import re
import threading
import time

def pytest_collect_file(parent, path):
    if path.ext == ".oot" and path.basename.startswith("test"):
        return TestCaseFile(path, parent)

class TestCaseFile(pytest.File):
    # test_bed: the test bed file
    # test_cases: an array of the test cases

    def collect(self):
        suite_content = self.fspath.open().read()
        self.__parse_suite(suite_content)

        # Import objects in the test bed
        if self.test_bed != None:
            #self.objs = __import__(self.test_bed, globals())
            import importlib
            self.objs = importlib.import_module("systemtest.test." + self.test_bed)

        for case in self.cases:
            line1_end = case.find('\n')
            line1 = case[0:line1_end].strip()
            steps = case[line1_end:]
            m = re.match(r'(\w+)\s*\((.*)\)', line1)
            (case_id, case_dec) = m.group(1,2)
            yield TestCaseItem(case_id, self, case_dec, steps)

    def __parse_suite(self, suite_content):
        ''' To parse the system case file, see detail of the system test file example
        :param suite_content: The content of the test case file.
        :return: no return, exception will be raised if the format is not right
        '''

        # split cases, notice that the first element of the cases is about the test suite description
        cases = suite_content.split("\ncase_")

        # Deal with the test suite description; cases[0] is about the test suite summary
        self.name = 'unknown'
        self.test_bed = None
        self.suite_attr = {}
        self.cases = cases[1:]
        lines = cases[0].split("\n")
        for line in lines:
            line = line.strip()
            if len(line) == 0: continue
            if line[0] == '#': continue
            colon = line.find(':')
            if colon == -1: continue
            (name, spec) = (line[0:colon], line[colon+1:].strip())
            if name == 'test_suite':
                self.name = spec
            elif name == 'test_bed':
                self.test_bed = spec
            else:
                self.suite_attr[name] = spec


class TestCaseItem(pytest.Item):
    ''' A case structure, one case can contain multiple steps
    '''
    def __init__(self, name, parent, dec, steps):
        super(TestCaseItem, self).__init__(name, parent)
        self.dec = dec
        self.steps = steps

    def runtest(self):
        steps_l = self.steps.split('\n')
        for step in steps_l:
            step = step.strip()
            if len(step) == 0: continue
            if step[0] == '#': continue
            step_obj = TestStep(step, self) # To create a step_obj with parsing
            step_obj.execute()
            #if step == '': raise TestException(self, self.name, step)

    def repr_failure(self, excinfo):
        """ called when self.runtest() raises an exception. """
        if isinstance(excinfo.value, TestStepFail):
            return "\n".join([
            "usecase execution failed",
            " failed step: %r: %r" % excinfo.value.args[1:3]
            ])

    def reportinfo(self):
        ''' Called when there is a failure as a failed case title'''
        return self.fspath, 0, "case_%s (%s)" % (self.name, self.dec)


class TestStep:
    '''A test step class, to deal with all test step related actions'''
    def __init__(self, step_string, testCase):
        self.objs = testCase.parent.objs
        #self.obj   # the obj string
        #self.method    # the method string
        self.func = None  # the actual function object to be invoked (not the string)
        self.params = ()    # the list of parameters
        self.step_string = step_string
        self.parent = testCase
        self.op = None
        self.exp_value = None
        self.options = {
            # 0: no timeout setting; others, raise Timeout exception if no return in Timeout seconds
            # --timeout   == -t
            "Timeout": 0,

            # 0: no duration setting; Stay on this step for xxx seconds if not 0
            # --duration == -d
            "Duration": 0,

            # Ture: this step is expected to fail
            # --expectedfailure  == -x
            "ExpectedFailure": False,

            # Repeat this step until expected value returned, the number setting means timeout seconds
            # --repeat  == -r
            "RepeatInSeconds": 0,

            # To skip this step
            # --skip  == -s
            "Skip": False
        }
        self.parse()

    def execute(self):
        if self.options["Skip"]: return
        end_time = time.time() + self.options["Duration"]
        if self.options["Timeout"] > 0 :
            t = threading.Thread(target = self.__execute)
            t.start()
            t.join(self.options["Timeout"])
            if t.is_alive():
                raise TestStepFail(self, self.step_string, "Timeout")
        else:
            self.__execute()

        ## Deal with the Duration Options
        wait_seconds = end_time - time.time()
        if wait_seconds >0: time.sleep(wait_seconds)


    def __execute(self):
        if self.options["RepeatInSeconds"] > 0:
            end_time = time.time() + self.options["RepeatInSeconds"]
            while (time.time() < end_time) :
                self.ret = self.func(*self.params)
                if self.__step_pass() :
                    return
                time.sleep(1)
            raise TestStepFail(self, self.step_string, self.ret)
        else :
            self.ret = self.func(*self.params)
            if not self.__step_pass():
                raise TestStepFail(self, self.step_string, self.ret)


    def __step_pass(self):  # deal with the ExpectedFailure option
        if not self.op: return True
        if self.options["ExpectedFailure"] :
            return (not self.step_pass())
        else :
            return self.step_pass()

    def step_pass(self):
        ret_val = self.ret
        if self.exp_value == None: #There is an operator, but no expected value
            raise TestRunTimeError(self, self.step_string, ret_val)

        if isinstance(ret_val, str):
            if self.op in ['=~', '!=']:
                l = re.compile(self.exp_value).find(ret_val)
                return True if (self.op == '=~' and l) or (self.op == '!~' and not l) else False
            else: # for ==, !=, <, >, <= and >= of strings
                return eval('ret_val' + self.op + self.exp_value)
        elif isinstance(ret_val, float):
            import math
            try:
                exp_value_f = float(self.exp_value)            # The expected result is a number?
            except ValueError:
                raise TestRunTimeError(self, self.step_string, "expected value is expected to be a float")
            if self.op in ['<', '<=', '>', '>=']:
                return eval('ret_val' + self.op + 'exp_value_f')
            elif self.op == '==': # to see if they are very close
                return math.fabs(ret_val - exp_value_f) < 1.0e-6  # precise 1.0e-6
            elif self.op == '!=' :
                return math.fabs(ret_val - exp_value_f) > 1.0e-6  # precise 1.0e-6
            else:
                raise TestRunTimeError(self, self.step_string, "Wrong operator for a float")
        elif isinstance(ret_val, int):
            if not re.compile(r"\d*(\.\d+)?").match(self.exp_value):
                raise TestRunTimeError(self, self.step_string, "expected value is expected to be a integer")
            if self.op in ['<', '<=', '>', '>=', '==', '!=']:
                return eval('ret_val' + self.op + self.exp_value)
            else:
                raise TestRunTimeError(self, self.step_string, "Wrong operator for a float")


    def parse(self):
        regex = re.compile(r'(\w+)\.(\w+)\s*(\(.*\))(.*)$')
        m = regex.match(self.step_string)
        (self.obj, self.method, param_str, p_f) = m.group(1,2,3,4)
        obj = getattr(self.objs, self.obj)
        self.func = getattr(obj, self.method)
        try: #if wrong, just keep null list
            self.params = eval(param_str[0:-1] + ",)", self.objs.__dict__, {})  # the list of parameters
        except:
            self.params = ()
        p_f = p_f.strip()

        if len(p_f) != 0 and p_f[0] != '#':
            try:
                m = re.compile(r'(==|!=|<=|>=|<|>|=~|!~)\s*(\"[^\"]+\"|\'[^\']+\'|\S+)(.*)$').match(p_f)
                (self.op, self.exp_value, options) = m.group(1,2,3)
                options = options.strip()
            except:
                options = p_f

            if len(options) != 0 and options[0] != '#':
                ol = re.compile(r'(?<!^)\s+(?=(?:-\w|--\w{2,}))').split(options)
                for o in ol:
                    if o[0] != '-' :
                        raise TestRunTimeError(self, self.step_string, "wrong options: "+o)
                    if o[1] == '-': # It is a long option string
                        r = re.compile(r'--(\w+)\s*(\S*)$').match(o)
                        if r.group(1) == "timeout":
                            self.options['Timeout'] = int(r.group(2))
                        elif r.group(1) == "duration":
                            self.options['Duration'] = int(r.group(2))
                        elif r.group(1) == 'expectedfailure':
                            if len(r.group(2))==0 or r.group(2)[0] in "TtYy":
                                self.options['ExpectedFailure'] = True
                        elif r.group(1) == 'skip':
                            if len(r.group(2))==0 or r.group(2)[0] in "TtYy":
                                self.options['Skip'] = True
                        elif r.group(1) == 'repeat' :
                            self.options['RepeatInSeconds'] = int(r.group(2))
                        else: raise TestRunTimeError(self, self.step_string, "wrong options: "+o)
                    else:
                        key = o[1]
                        if len(o) > 2: value = o[2:].strip()
                        else: value = ''
                        if key == "t":
                            self.options['Timeout'] = int(value)
                        elif key == "d":
                            self.options['Duration'] = int(value)
                        elif key == 'x':
                            if len(value)==0 or value[0] in "TtYy":
                                self.options['ExpectedFailure'] = True
                        elif key == 's':
                            if len(value)==0 or value[0] in "TtYy":
                                self.options['Skip'] = True
                        elif key == 'r' :
                            self.options['RepeatInSeconds'] = int(value)
                        else: raise TestRunTimeError(self, self.step_string, "wrong options: "+o)

class TestStepFail(Exception):
    """ custom exception for error reporting. """

class TestRunTimeError(Exception):
    """ custom exception for error reporting. """

