"""Use a script to retrieve the versions."""
import os
import subprocess
from ..errors import VersionError
from .base import Detector, Version


class ScriptDetector(Detector):
    """
    Use each line of the output of the executable ``version`` file in the container directory as
    versions. Discards blank lines. All versions returned by this detector are unverified.
    """

    def detect(self):
        """Yield the versions output by the script. Raise ``VersionError`` on script failure."""
        cmd = os.path.join(self.container.path, 'version')
        if not os.path.isfile(cmd) or not os.access(cmd, os.X_OK):
            return

        env = os.environ.copy()
        env = env.update({
            'CONTAINER_PATH': self.container.path,
            'CONTAINER_NAME': self.container.name,
            'CONTAINER_USER': self.container.user,
        })

        try:
            out = subprocess.check_output(['bash', '-c', cmd], cwd=self.container.path, env=env)
            for line in out.split('\n'):
                if line:
                    yield Version(line, False)
        except subprocess.CalledProcessError:
            raise VersionError("version script failed: command failed")
