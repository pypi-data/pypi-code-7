import subprocess
import unittest

from mockprocess import MockCheckOutput


class TestMockCheckOutput(unittest.TestCase):
    def test_raises_exception(self):
        exit_code = 1
        cmd = ['/bin/false']
        output = None
        message = 'Command \'{cmd}\' returned non-zero exit status {returncode}'

        with MockCheckOutput(output, exit_code):
            try:
                subprocess.check_output(cmd)
            except subprocess.CalledProcessError as exp:
                self.assertEqual(exp.returncode, exit_code)
                self.assertEqual(exp.output, output)
                self.assertListEqual(exp.cmd, cmd)

                expected = message.format(cmd=cmd, returncode=exit_code)
                self.assertEqual(str(exp), expected)
            else:
                self.fail('An exception was not raised')


    def test_basic_output(self):
        with MockCheckOutput('line\n'):
            output = subprocess.check_output([])

            self.assertEqual(output, 'line\n')


    def test_additional_arguments(self):
        with MockCheckOutput('ok\n'):
            output = subprocess.check_output('', stderr=subprocess.PIPE)

            self.assertEqual(output, 'ok\n')
