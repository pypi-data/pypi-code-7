__author__ = 'Ruben Nielsen'

import random

import tempfile
import shutil

from backup2.helpers import *
from backup2.backup_runner import *

from unittest.case import TestCase


def read_file(filename, mode="rb"):
    with open(filename, mode) as f:
        return f.read()


class GoodOp(Operation):
    def run_test1(self):
        return


class GoodOp2(Operation):
    def run_test2(self):
        return


class BadOp(Operation):
    def run_test2(self):
        return 1/0


class BaseTestCase(TestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.tempdir = tempfile.gettempdir()
        self.working_dir = self.tempdir + '/tests'
        try:
            shutil.rmtree(self.working_dir)
        except:
            pass
        try:
            os.makedirs(self.working_dir)
        except:
            pass


class BackupRunnerTest(BaseTestCase):
    def test_can_create_instance(self):
        runner = BackupRunner(silent=True)
        self.assertTrue(bool(runner))


class RegisterTest(BaseTestCase):
    def test_can_register_dictionary(self):
        runner = BackupRunner()
        runner.register({
            'test1': GoodOp()
        })
        self.assertTrue(bool(runner.operations))

    def test_register_only_accepts_dict(self):
        runner = BackupRunner(silent=True)
        with self.assertRaises(ValueError, msg="Did not raise ValueError as expected"):
            runner.register(42)

    def test_register_only_accepts_dicts_with_operations(self):
        runner = BackupRunner(silent=True)
        with self.assertRaises(ValueError, msg="Did not raise ValueError as expected"):
            runner.register({
                'test1': None
            })


class RunTest(BaseTestCase):
    def test_can_run_all_ops(self):
        runner = BackupRunner(silent=True)
        runner.register({
            'test1': GoodOp(),
            'test2': GoodOp2(),
        })
        runner.run()
        out = runner.get_summary()
        self.assertTrue(out['test1'][0]['method_name'].startswith('(SUCCESS)'), out['test1'][0]['method_name'])
        self.assertTrue(out['test2'][0]['method_name'].startswith('(SUCCESS)'), out['test2'][0]['method_name'])

    def test_can_run_selected_ops(self):
        runner = BackupRunner(silent=True)
        runner.register({
            'test1': GoodOp(),
            'test2': GoodOp2(),
        })
        runner.run(['test1'])
        out = runner.get_summary()

        self.assertTrue(out['test1'][0]['method_name'].startswith('(SUCCESS)'), out['test1'][0]['method_name'])
        self.assertFalse(out['test2'][0]['method_name'].startswith('(SUCCESS)'), out['test2'][0]['method_name'])


class CommandLineTest(BaseTestCase):
    def test_command_line_rejects_invalid_operations(self):
        runner = BackupRunner(silent=True)
        runner.register({
            'test1': GoodOp(),
            'test2': GoodOp2(),
        })
        out = runner.get_command_line_tool('test1', 'test3')
        self.assertFalse(out)

    def test_command_line_rejects_invalid_options(self):
        runner = BackupRunner(silent=True)
        runner.register({
            'test1': GoodOp(),
            'test2': GoodOp2(),
        })
        runner.get_command_line_tool('test1', '--foobar')
        out = runner.get_summary()
        self.assertFalse(out)

    def test_command_line_accepts_valid_operations(self):
        runner = BackupRunner(silent=True)
        runner.register({
            'test1': GoodOp(),
            'test2': GoodOp2(),
        })
        runner.get_command_line_tool('test1', '--verbose')
        out = runner.get_summary()
        self.assertTrue(out)

    def test_summary_print(self):
        runner = BackupRunner(silent=True)
        runner.register({
            'test1': GoodOp(),
            'test2': GoodOp2(),
        })
        runner.run()


class EmailTest(BaseTestCase):
    def test_cannot_send_email_if_not_configured(self):
        runner = BackupRunner(silent=True)
        with self.assertRaises(ValueError):
            runner.send_email("msg", "subject", "mail@example.com")

    def test_can_send_email_if_configured(self):
        runner = BackupRunner(silent=True)
        runner.configure_email('foo', 'bar', 'baz', '1234')
        runner.send_email("msg", "subject", "mail@example.com")
        # No errors thrown


class UsageTest(BaseTestCase):
    def test_usage_returns_true_despite_errors(self):
        # When --help or -h is given, no operations are run. Only usage is printed.
        runner = BackupRunner(silent=True)
        runner.register({
            'test1': BadOp(),
        })
        runner.get_command_line_tool('test1', '--help')
        out = runner.get_summary()
        self.assertEqual({}, out)
        runner.get_command_line_tool('test1', '-h')
        out = runner.get_summary()
        self.assertEqual({}, out)


class CallTest(BaseTestCase):
    def setUp(self):
        self.helper = HelperMixin()

    def test_call_properly_raises_exception(self):
        with self.assertRaises(CallFailedError):
            self.helper.call('echo "test"', accepted_return_codes=[1, 2, 3])

    def test_calls_properly(self):
        result, _, _ = self.helper.call('echo "test"')
        self.assertEqual(
            b"test\n",
            result
        )


class TarFolderTest(BaseTestCase):
    def setUp(self):
        super(TarFolderTest, self).setUp()
        self.helper = HelperMixin()
        self.helper.call('mkdir -p             %s/tar_folder' % self.working_dir)
        self.helper.call('echo "foobar"      > %s/tar_folder/file1.txt' % self.working_dir)
        self.helper.call('echo "Hello world" > %s/tar_folder/file2.txt' % self.working_dir)

    def test_can_tar_folder_without_trailing_slash(self):
        # tar_folder should have same behaviour whether the source folder has a trailing slash or not
        target = "%s/tar_file.tar.gz" % self.working_dir
        self.helper.tar_folder("%s/tar_folder" % self.working_dir, target)
        self.assertTrue(
            os.path.isfile(target)
        )

    def test_can_tar_folder_with_trailing_slash(self):
        # tar_folder should have same behaviour whether the source folder has a trailing slash or not
        target = "%s/tar_file.tar.gz" % self.working_dir
        self.helper.tar_folder("%s/tar_folder/" % self.working_dir, target)
        self.assertTrue(
            os.path.isfile(target)
        )


class UntarFolderTest(BaseTestCase):
    def setUp(self):
        super(UntarFolderTest, self).setUp()
        self.helper = HelperMixin()
        self.helper.call('mkdir -p             %s/tar_folder' % self.working_dir)
        self.helper.call('echo "foobar"      > %s/tar_folder/file1.txt' % self.working_dir)
        self.helper.call('echo "Hello world" > %s/tar_folder/file2.txt' % self.working_dir)
        self.tar_file = "%s/tar_file.tar.gz" % self.working_dir
        self.helper.tar_folder("%s/tar_folder" % self.working_dir, self.tar_file)
        self.helper.call('rm -rf               %s/tar_folder' % self.working_dir)

    def test_can_untar_folder(self):
        # tar_folder should have same behaviour whether the source folder has a trailing slash or not
        target = "%s/" % self.working_dir
        self.helper.untar_folder(self.tar_file, target)
        self.assertTrue(
            os.path.isdir(target)
        )


class EncryptionTest(BaseTestCase):
    def setUp(self):
        super(EncryptionTest, self).setUp()
        self.helper = HelperMixin()

    def test_can_encrypt_and_decrypt(self):
        source_file = "%s/source.txt" % self.working_dir
        enc_file = "%s/enc.txt" % self.working_dir
        plain_file = "%s/plain.txt" % self.working_dir
        secret_key = "068788e1-9c86-49b1-9bb4-0cec9e6a081e"

        with open(source_file, 'wb') as f:
            bytes = ''.join([chr(random.randint(48, 122)) for _ in range(32 * 1024)]).encode()
            f.write(bytes)

        self.helper.encrypt_file(source_file, enc_file, secret_key)
        self.helper.decrypt_file(enc_file, plain_file, secret_key)

        self.assertNotEqual(
            read_file(source_file),
            read_file(enc_file)
        )
        self.assertEqual(
            read_file(source_file),
            read_file(plain_file)
        )


class IterateClassMethodTest(BaseTestCase):
    """
    Test that it is possible to loop target class' attributes
    """
    def test_can_iterate_over_class_methods(self):
        class Foo():
            def run_foo(self):
                pass

            def run_bar(self):
                pass

            def foo_bar(self):
                pass

        import inspect


        methods = [(k, v) for k, v in inspect.getmembers(Foo) if k.startswith('run_')]

        self.assertEqual(
            2,
            len(methods)
        )

        self.assertIn(
            'run_foo',
            [k for k, v in methods]
        )

        self.assertIn(
            'run_bar',
            [k for k, v in methods]
        )

        self.assertNotIn(
            'foo_bar',
            [k for k, v in methods]
        )


class IterateSelfMethodTest(BaseTestCase):
    """
    Test that it is possible for a class to loop over its own methods
    """
    def run_foo(self):
        pass

    def run_bar(self):
        pass

    def foo_bar(self):
        pass

    def __dir__(self):
        return [
            'run_foo',
            'run_bar',
            'foo_bar',
        ]

    def test_can_iterate_over_class_attributes(self):
        self.assertIn(
            'run_foo',
            dir(self)
        )

        # Apparantly, dir() gets the list in reverse order
        methods = [x for x in reversed([k for k in dir(self) if k.startswith('run_')])]

        self.assertEqual(
            2,
            len(methods)
        )

        self.assertIn(
            'run_foo',
            methods
        )

        self.assertIn(
            'run_bar',
            methods
        )

        self.assertNotIn(
            'foo_bar',
            methods
        )

        self.assertEqual(
            'run_foo',
            methods[0]
        )

        self.assertEqual(
            'run_bar',
            methods[1]
        )
