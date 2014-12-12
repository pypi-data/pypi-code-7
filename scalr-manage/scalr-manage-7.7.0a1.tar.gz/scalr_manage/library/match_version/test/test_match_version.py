# coding:utf-8
import os
from scalr_manage.version import __version__
from scalr_manage.library.match_version.target import MatchVersionTarget
from scalr_manage.test.util import BaseWrapperTestCase


class MatchVersionTestCase(BaseWrapperTestCase):
    def setUp(self):
        super(MatchVersionTestCase, self).setUp()

        self.target = MatchVersionTarget()
        self.target.register(self.parser)

    def test_match_version(self):
        for version, exit_code in [
            (__version__, 0),
            ("...", 1),
            ("a.b.c", 1)
        ]:
            cnf = os.path.join(self.work_dir, version + ".json")

            with open(cnf + ".version", "w") as f:
                f.write(version)

            try:
                args = self.parser.parse_args(["--configuration", cnf])
                self.target.__call__(args, self.ui, self.tokgen)
            except SystemExit as e:
                self.assertEqual(exit_code, e.code)
            else:
                self.fail("SystemExit wasn't raised!")

    def test_no_version(self):
        try:
            args = self.parser.parse_args([])
            self.target.__call__(args, self.ui, self.tokgen)
        except SystemExit as e:
            self.assertEqual(1, e.code)
        else:
            self.fail("SystemExit wasn't raised!")
