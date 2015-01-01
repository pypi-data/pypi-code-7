"""
This is to implement a function called step(), and a bunch-function steps() or s():
The format of a step looks like:
    obj.method(parameter) op exp-value options
In this one step, there is an action, and also a check point
This one step can be translated to multiple lines of python code,
or dozens lines of code if there is one option or multiple options.

Examples (Quick Start):
1.  step("num1.add(3,4,5) == 23")
    the same as:
        assert num1.add(3,4,5) == 23
very simple, right?

2.  step("string1.range(1..4) !~ r'\w\-\w'")
    Perl-like condition, =~ means 'contains', and !~ means 'not contains'
            btw, regex can be used
    The step is like:
        import re
        assert re.compile(r'\w\-\w').find(string1.range(1..4))

3.  step("num_async.data_sync() -t 15")
    a little complicated, -t means timeout. In this step, a time-out timer is set to 15 seconds.
    It means this step is allowed to be completed in 15 seconds, otherwise, it fails.
    no op (==, <, >, =~, etc.) in this step, it means no assert required to check the return value

    This is implemented by forking another thread to run the step.
    Considering some tests require to wait for a response, but how long? this can be useful

4.  step("num_async.get_value() == 500 --repeat 20")
    Another option --repeat (same as -r).
    The step means the step will be re-run every another second in total 20 seconds,
        until the condition comes true
    If the condition is always false in 20 seconds, then the step fails

5.  step("num2.multiple(4,5) == 460 -x True -t 12 -r 10")
    Multiple options for one step.
        -x (--expectedfail): pass if the condition is not met
        -t (--timeout): set a timeout timer
        -r (--repeat): repeat this step in 10 seconds until it comes true(here false actually due to -x), or timeout
6.  steps('''
        num1.add(4)
        num2.add(3,4,5,6) == 23
        num2.multiple(4,5) == 460 -x True -t 12 -r 10
        num3.add(3,4,var2) == 1000 --skip -t 25
    ''')
    multiple steps in one shot

"""


__author__ = 'Steven LI'



